from typing import Optional, Dict, Any
from django.db import models
from decimal import Decimal, InvalidOperation

from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct

class SubproductRepository:
    """
    Repositorio fino para Subproduct.
    - La validación de negocio vive en serializers/services.
    - Auditoría via BaseModel.save(user=...).
    - El stock se maneja en la app 'stocks'.
    """

    @staticmethod
    def get_by_id(subproduct_id: int) -> Optional[Subproduct]:
        """Recupera un subproducto ACTIVO por ID."""
        try:
            return (
                Subproduct.objects
                .select_related('parent', 'created_by')
                .get(id=subproduct_id, status=True)
            )
        except Subproduct.DoesNotExist:
            return None

    @staticmethod
    def get_all_active(parent_product_id: int) -> models.QuerySet:  # QuerySet[Subproduct]
        """
        Subproductos activos de un padre (ordenado por Meta: -created_at).
        """
        return (
            Subproduct.objects
            .filter(parent_id=parent_product_id, status=True)
            .select_related('parent', 'created_by')
        )

    @staticmethod
    def exists_active_same_number_coil(parent: Product, number_coil: str, exclude_id: Optional[int] = None) -> bool:
        """
        ¿Existe un subproducto ACTIVO con el mismo número de bobina para este padre?
        Comparación case-insensitive.
        """
        qs = Subproduct.objects.filter(parent=parent, number_coil__iexact=str(number_coil).strip(), status=True)
        if exclude_id is not None:
            qs = qs.exclude(id=exclude_id)
        return qs.exists()

    @staticmethod
    def create(user, parent: Product, **data: Any) -> Subproduct:
        if not isinstance(parent, Product) or not parent.status:
            raise ValueError("El producto padre no es válido o no está activo.")

        data.pop('quantity', None)

        if 'initial_stock_quantity' not in data:
            raise ValueError("initial_stock_quantity es obligatorio y debe ser > 0.")
        try:
            qty = Decimal(str(data['initial_stock_quantity']))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("initial_stock_quantity debe ser numérico.")
        if qty <= 0:
            raise ValueError("initial_stock_quantity debe ser mayor a 0.")

        # number_coil como string (trim) y unicidad por padre (case-insensitive)
        if 'number_coil' in data:
            raw_nc = data.get('number_coil')
            nc = None if raw_nc is None else str(raw_nc).strip()
            data['number_coil'] = nc or None
            if nc and SubproductRepository.exists_active_same_number_coil(parent, nc):
                raise ValueError("Ya existe un subproducto activo con ese número de bobina para este producto.")

        # coherente con la view: nace activo si qty > 0
        data['status'] = qty > 0

        instance = Subproduct(parent=parent, **data)
        instance.save(user=user)
        return instance

    @staticmethod
    def update(instance: Subproduct, user, data: Dict[str, Any]) -> Subproduct:
        allowed_fields = {
            'brand', 'number_coil', 'initial_enumeration', 'final_enumeration',
            'gross_weight', 'net_weight', 'initial_stock_quantity',
            'location', 'technical_sheet_photo', 'form_type', 'observations'
        }

        # si viene number_coil y cambia, verificar unicidad (string, case-insensitive)
        if 'number_coil' in data and data['number_coil'] is not None:
            new_nc_raw = data['number_coil']
            new_nc = str(new_nc_raw).strip()
            if new_nc == "":
                new_nc = None
            if new_nc != getattr(instance, 'number_coil', None):
                if new_nc and SubproductRepository.exists_active_same_number_coil(instance.parent, new_nc, exclude_id=instance.pk):
                    raise ValueError("Ya existe un subproducto activo con ese número de bobina para este producto.")
                data['number_coil'] = new_nc

        changed_fields = []
        for field, value in data.items():
            if field in allowed_fields and getattr(instance, field) != value:
                setattr(instance, field, value)
                changed_fields.append(field)

        if changed_fields:
            instance.save(user=user, update_fields=changed_fields + ['modified_at', 'modified_by'])
        return instance

    @staticmethod
    def soft_delete(instance: Subproduct, user) -> Subproduct:
        """
        Baja lógica (usa BaseModel.delete para auditoría).
        """
        if not isinstance(instance, Subproduct):
            raise ValueError("Se requiere una instancia válida de Subproduct.")
        instance.delete(user=user)
        return instance
