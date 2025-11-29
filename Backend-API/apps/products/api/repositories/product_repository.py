from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from apps.products.models.product_model import Product
from apps.products.models.category_model import Category

class ProductRepository:
    """
    Repositorio para Product. Delega lógica de save/delete/auditoría a BaseModel.
    El stock se maneja en la app 'stock'.
    """

    @staticmethod
    def get_all_active_products():
        """Obtener todos los productos activos."""
        return Product.objects.filter(status=True).select_related('category','created_by')

    @staticmethod
    def get_by_id(product_id: int) -> Product | None:
        """Obtener un producto activo por su ID."""
        try:
            return Product.objects.select_related('category', 'created_by').get(id=product_id, status=True)
        except Product.DoesNotExist:
            return None

    @staticmethod
    def create(
        name: str,
        category_id: int,
        user=None,
        code: str | None = None,
        brand: str | None = None,
        location: str | None = None,
        position: str | None = None,
        has_subproducts: bool = False,
        price: float | None = None,
        last_purchase_cost: float | None = None,
        unit: str | None = None,
        min_stock: float | None = None,
        detail_internal: str | None = None,
        detail_public: str | None = None,
        vat_condition_code: int | None = None,
    ) -> Product:
        """
        Crea un nuevo producto usando la lógica de BaseModel.save.
        """
        # 🧱 Verificamos la categoría obligatoria
        try:
            category_instance = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise ValueError(f"La categoría con ID {category_id} no existe.")

        # Validaciones mínimas de negocio para valores numéricos
        if price is not None and price < 0:
            raise ValidationError("El precio no puede ser negativo.")
        if last_purchase_cost is not None and last_purchase_cost < 0:
            raise ValidationError("El costo de compra no puede ser negativo.")
        if min_stock is not None and min_stock < 0:
            raise ValidationError("El stock mínimo no puede ser negativo.")

        # 🛠️ Instanciamos el producto con todos los campos relevantes
        product_instance = Product(
            code=code,
            name=name,
            price=price,
            last_purchase_cost=last_purchase_cost,
            unit=unit,
            min_stock=min_stock,
            detail_internal=detail_internal,
            detail_public=detail_public,
            vat_condition_code=vat_condition_code,
            brand=brand,
            location=location,
            position=position,
            category=category_instance,
            has_subproducts=has_subproducts,
        )
        product_instance.save(user=user)
        return product_instance


    @staticmethod
    def update(
        product_instance: Product,
        user,
        name: str = None,
        category_id: int = None,
        code: str | None = None,
        brand: str | None = None,
        location: str | None = None,
        position: str | None = None,
        has_subproducts: bool | None = None,
        price: float | None = None,
        last_purchase_cost: float | None = None,
        unit: str | None = None,
        min_stock: float | None = None,
        detail_internal: str | None = None,
        detail_public: str | None = None,
        vat_condition_code: int | None = None,
    ) -> Product:
        """
        Actualiza un producto usando la lógica de BaseModel.save.
        """
        changes_made = False

        if name is not None and product_instance.name != name:
            product_instance.name = name
            changes_made = True
        if brand is not None and product_instance.brand != brand:
            product_instance.brand = brand
            changes_made = True
        if code is not None and product_instance.code != code:
            product_instance.code = code
            changes_made = True
        if location is not None and product_instance.location != location:
            product_instance.location = location
            changes_made = True
        if position is not None and product_instance.position != position:
            product_instance.position = position
            changes_made = True
        if has_subproducts is not None and product_instance.has_subproducts != has_subproducts:
            product_instance.has_subproducts = has_subproducts
            changes_made = True

        # Campos numéricos y de detalle
        if price is not None and product_instance.price != price:
            if price < 0:
                raise ValidationError("El precio no puede ser negativo.")
            product_instance.price = price
            changes_made = True

        if last_purchase_cost is not None and product_instance.last_purchase_cost != last_purchase_cost:
            if last_purchase_cost < 0:
                raise ValidationError("El costo de compra no puede ser negativo.")
            product_instance.last_purchase_cost = last_purchase_cost
            changes_made = True

        if min_stock is not None and product_instance.min_stock != min_stock:
            if min_stock < 0:
                raise ValidationError("El stock mínimo no puede ser negativo.")
            product_instance.min_stock = min_stock
            changes_made = True

        if unit is not None and product_instance.unit != unit:
            product_instance.unit = unit
            changes_made = True

        if detail_internal is not None and product_instance.detail_internal != detail_internal:
            product_instance.detail_internal = detail_internal
            changes_made = True

        if detail_public is not None and product_instance.detail_public != detail_public:
            product_instance.detail_public = detail_public
            changes_made = True

        if vat_condition_code is not None and product_instance.vat_condition_code != vat_condition_code:
            product_instance.vat_condition_code = vat_condition_code
            changes_made = True

        # --- 🔁 FK: Categoría (obligatoria) ---
        if category_id is not None and product_instance.category_id != category_id:
            try:
                product_instance.category = Category.objects.get(pk=category_id)
                changes_made = True
            except Category.DoesNotExist:
                raise ValueError(f"La categoría con ID {category_id} no existe.")

        if changes_made:
            product_instance.save(user=user)

        return product_instance

    @staticmethod
    def soft_delete(product_instance: Product, user) -> Product:
        """Realiza un soft delete usando la lógica de BaseModel.delete."""
        if not isinstance(product_instance, Product):
             raise ValueError("Se requiere una instancia de Product válida.")
        product_instance.delete(user=user)
        return product_instance
