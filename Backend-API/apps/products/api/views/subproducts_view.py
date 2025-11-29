import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models import DecimalField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.core.pagination import Pagination
from apps.core.utils import broadcast_crud_event
from apps.products.api.serializers.subproduct_serializer import SubProductSerializer
from apps.products.docs.subproduct_doc import (
    create_subproduct_doc,
    delete_subproduct_by_id_doc,
    get_subproduct_by_id_doc,
    list_subproducts_doc,
    update_subproduct_by_id_doc,
)
from apps.products.filters.subproduct_filter import SubproductFilter
from apps.products.models.product_model import Product
from apps.products.models.subproduct_model import Subproduct
from apps.stocks.models import SubproductStock
from apps.stocks.services import (
    adjust_subproduct_stock,
    sync_parent_product_stock,
    initialize_subproduct_stock,
)
from apps.stocks.services.status import ensure_subproduct_status_from_stock  # ✅ import correcto
from apps.products.utils.cache_keys import (
    PRODUCT_DETAIL_CACHE_PREFIX,
    PRODUCT_LIST_CACHE_PREFIX,
    SUBPRODUCT_DETAIL_CACHE_PREFIX,
    SUBPRODUCT_LIST_CACHE_PREFIX,
)
from apps.products.utils.cache_invalidation import invalidate_subproduct_cache

logger = logging.getLogger(__name__)

# ── CACHE CONFIG ─────────────────────────────────────────────
LIST_TTL = 60 * 15   # 15 minutos
DETAIL_TTL = 60 * 5  # 5 minutos

list_cache = (
    cache_page(LIST_TTL, key_prefix=SUBPRODUCT_LIST_CACHE_PREFIX)
    if not settings.DEBUG else (lambda fn: fn)
)
detail_cache = (
    cache_page(DETAIL_TTL, key_prefix=SUBPRODUCT_DETAIL_CACHE_PREFIX)
    if not settings.DEBUG else (lambda fn: fn)
)


@extend_schema(
    summary=list_subproducts_doc["summary"],
    description=list_subproducts_doc["description"] + "\n\nTTL=15min.",
    tags=list_subproducts_doc["tags"],
    operation_id=list_subproducts_doc["operation_id"],
    parameters=list_subproducts_doc["parameters"],
    responses=list_subproducts_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@list_cache
def subproduct_list(request, prod_pk):
    """
    Lista subproductos de un producto padre (por defecto solo activos), con paginación y stock actual.
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)

    base_qs = (
        Subproduct.objects.filter(parent=parent)
        .select_related("parent", "created_by")
    )

    stock_sq = (
        SubproductStock.objects
        .filter(subproduct=OuterRef("pk"), status=True)
        .values("quantity")[:1]
    )

    qs = base_qs.annotate(
        current_stock_val=Subquery(
            stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    ).annotate(
        current_stock=Coalesce(
            "current_stock_val",
            Decimal("0.00"),
            output_field=DecimalField(max_digits=15, decimal_places=2),
        )
    )

    # Filtros
    filt = SubproductFilter(request.GET, queryset=qs)
    if not filt.is_valid():
        return Response(filt.errors, status=status.HTTP_400_BAD_REQUEST)
    qs = filt.qs

    # Default: si no vino 'status', mostrar solo activos
    if "status" not in request.GET:
        qs = qs.filter(status=True)

    paginator = Pagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(qs, request)
    data = SubProductSerializer(
        page, many=True, context={"request": request, "parent_product": parent}
    ).data
    return paginator.get_paginated_response(data)


@extend_schema(
    summary=create_subproduct_doc["summary"],
    description=create_subproduct_doc["description"] + "\n\nInvalidará caché de lista y detalle tras CREATE.",
    tags=create_subproduct_doc["tags"],
    operation_id=create_subproduct_doc["operation_id"],
    request=create_subproduct_doc["request"],
    responses=create_subproduct_doc["responses"],
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_subproduct(request, prod_pk):
    """
    - Stock inicial es OBLIGATORIO y debe ser > 0; si no, se rechaza la creación.
    - El estado (`status`) se sincroniza automáticamente por servicios según el stock.
    - Además, al crear se inicializa como activo si el stock inicial > 0.
    - ⚠️ En endpoints de archivos de subproducto NO filtres por status=True (para poder adjuntar siempre).
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)

    data = request.data.copy()
    errors = {}

    # ── helpers parseo ───────────────────────────────────────────
    def to_str_nc(val, field):
        """Normaliza número de bobina como string (trim). Vacío -> None."""
        if val in (None, ""):
            return None
        s = str(val).strip()
        if not s:
            return None
        if len(s) > 50:
            errors.setdefault(field, []).append("Máximo 50 caracteres.")
        return s

    def to_decimal(val, field):
        if val in (None, ""):
            return None
        try:
            return Decimal(str(val))
        except (InvalidOperation, ValueError, TypeError):
            errors.setdefault(field, []).append("Formato numérico inválido.")
            return None

    # ── inputs ──────────────────────────────────────────────────
    brand  = (data.get("brand") or "").strip()
    number_coil = to_str_nc(data.get("number_coil"), "number_coil")  # ← ahora string normalizado
    initial_enumeration = to_decimal(data.get("initial_enumeration"), "initial_enumeration")
    final_enumeration   = to_decimal(data.get("final_enumeration"),   "final_enumeration")
    gross_weight = to_decimal(data.get("gross_weight"), "gross_weight")
    net_weight   = to_decimal(data.get("net_weight"),   "net_weight")
    initial_stock_quantity = to_decimal(data.get("initial_stock_quantity"), "initial_stock_quantity")
    location  = data.get("location") or "Deposito Principal"
    form_type = data.get("form_type") or "Bobina"
    observations = data.get("observations") or ""

    # ── validaciones ────────────────────────────────────────────
    # number_coil: unicidad por padre (case-insensitive)
    if number_coil:
        if Subproduct.objects.filter(parent=parent, number_coil__iexact=number_coil, status=True).exists():
            errors.setdefault("number_coil", []).append(
                "Ya existe un subproducto activo con ese número de bobina para este producto."
            )

    if initial_enumeration is not None and final_enumeration is not None:
        if final_enumeration < initial_enumeration:
            errors.setdefault("final_enumeration", []).append(
                "Debe ser mayor o igual a la enumeración inicial."
            )

    if gross_weight is not None and net_weight is not None:
        if net_weight > gross_weight:
            errors.setdefault("net_weight", []).append("No puede ser mayor que el peso bruto.")

    # Regla de negocio: obligatorio y > 0
    if initial_stock_quantity is None:
        errors.setdefault("initial_stock_quantity", []).append("Es obligatorio.")
    else:
        if initial_stock_quantity <= 0:
            errors.setdefault("initial_stock_quantity", []).append("Debe ser mayor a 0.")

    if form_type not in {"Bobina", "Rollo"}:
        errors.setdefault("form_type", []).append("Debe ser uno de: Bobina, Rollo.")

    if location not in {"Deposito Principal", "Deposito Secundario"}:
        errors.setdefault("location", []).append(
            "Debe ser uno de: Deposito Principal, Deposito Secundario."
        )

    if errors:
        raise DRFValidationError(errors)

    # Decidimos el estado inicial (activo si qty > 0)
    should_be_active = (initial_stock_quantity or Decimal("0")) > 0

    # ── persistencia ─────────────────────────────────────────────
    try:
        with transaction.atomic():
            subp = Subproduct(
                parent=parent,
                brand=brand,
                number_coil=number_coil,  # ← guardamos string (o None)
                initial_enumeration=initial_enumeration,
                final_enumeration=final_enumeration,
                gross_weight=gross_weight,
                net_weight=net_weight,
                initial_stock_quantity=initial_stock_quantity or Decimal("0"),
                location=location,
                form_type=form_type,
                observations=observations,
                status=should_be_active,  # nace activo si qty>0
            )
            subp.save(user=request.user)

            # Inicialización SINCRÓNICA del stock inicial (idempotente)
            try:
                initialize_subproduct_stock(
                    subproduct=subp,
                    user=request.user,
                    initial_quantity=initial_stock_quantity or Decimal("0.00"),
                    reason="Stock Inicial por Creación",
                )
            except Exception as e:
                logger.warning("No se pudo inicializar stock para subproducto %s: %s", subp.pk, e)

            # ✅ Asegurar estado desde el stock (evita depender de managers filtrados)
            try:
                ensure_subproduct_status_from_stock(subp, acting_user=request.user)
            except Exception as e:
                logger.warning("No se pudo asegurar status desde stock para subproducto %s: %s", subp.pk, e)

            # Si el producto aún no marcaba que tiene subproductos, márcalo ahora.
            if not getattr(parent, "has_subproducts", False):
                try:
                    parent.has_subproducts = True
                    try:
                        parent.save(user=request.user, update_fields=["has_subproducts", "modified_at", "modified_by"])
                    except TypeError:
                        parent.save(update_fields=["has_subproducts"])
                    logger.info("Producto %s marcado como has_subproducts=True", parent.pk)
                except Exception as e:
                    logger.warning("No se pudo marcar has_subproducts=True en Producto %s: %s", parent.pk, e)

            # Espejar stock del padre
            sync_parent_product_stock(parent, acting_user=request.user)

    except IntegrityError:
        return Response(
            {"number_coil": ["Ya existe un subproducto activo con ese número para este producto."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except (DRFValidationError, DjangoValidationError) as e:
        payload = (
            getattr(e, "detail", None)
            or getattr(e, "message_dict", None)
            or getattr(e, "messages", None)
        )
        if not payload:
            payload = {"detail": str(e) or "Validación inválida."}
        return Response(payload, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Error creando subproducto")
        err_cls = e.__class__.__name__
        err_msg = (str(e) or (e.args[0] if getattr(e, "args", None) else "") or repr(e) or "Error interno.")
        return Response({"detail": f"{err_cls}: {err_msg}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ── invalidar caché ─────────────────────────────────────────

    invalidate_subproduct_cache()

    # 🟢 Refrescar con _base_manager antes de serializar (por si el manager por defecto filtra)
    subp = Subproduct._base_manager.get(pk=subp.pk)

    data_out = SubProductSerializer(subp, context={"request": request, "parent_product": parent}).data
    broadcast_crud_event(
        event_type="create",
        app="products",
        model="Subproduct",
        data=data_out
    )
    return Response(data_out, status=status.HTTP_201_CREATED)


@extend_schema(
    summary=get_subproduct_by_id_doc["summary"],
    description=get_subproduct_by_id_doc["description"] + "\n\nTTL=5min.",
    tags=get_subproduct_by_id_doc["tags"],
    operation_id=get_subproduct_by_id_doc["operation_id"],
    parameters=get_subproduct_by_id_doc["parameters"],
    responses=get_subproduct_by_id_doc["responses"],
)
@extend_schema(
    summary=update_subproduct_by_id_doc["summary"],
    description=update_subproduct_by_id_doc["description"] + "\n\nInvalidará caché de lista y detalle tras UPDATE.",
    tags=update_subproduct_by_id_doc["tags"],
    operation_id=update_subproduct_by_id_doc["operation_id"],
    parameters=update_subproduct_by_id_doc["parameters"],
    request=create_subproduct_doc["request"],
    responses=update_subproduct_by_id_doc["responses"],
)
@extend_schema(
    summary=delete_subproduct_by_id_doc["summary"],
    description=delete_subproduct_by_id_doc["description"] + "\n\nInvalidará caché de lista y detalle tras DELETE.",
    tags=delete_subproduct_by_id_doc["tags"],
    operation_id=delete_subproduct_by_id_doc["operation_id"],
    parameters=delete_subproduct_by_id_doc["parameters"],
    responses=delete_subproduct_by_id_doc["responses"],
)
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def subproduct_detail(request, prod_pk, subp_pk):
    """
    GET: detalle cacheado (TTL=5min).
    PUT: actualiza subproducto (solo admins) + ajuste stock opcional + invalidación de caché.
    DELETE: baja suave (solo admins) + invalidación.
    """
    parent = get_object_or_404(Product, pk=prod_pk, status=True)

    # GET con cache_page (NO filtra por status: permite ver detalles aunque esté inactivo)
    if request.method == "GET":
        @detail_cache
        def cached_get(req, prod_id, subp_id):
            stock_sq = SubproductStock.objects.filter(
                subproduct=OuterRef("pk"), status=True
            ).values("quantity")[:1]
            qs = Subproduct.objects.annotate(
                current_stock_val=Subquery(
                    stock_sq, output_field=DecimalField(max_digits=15, decimal_places=2)
                )
            ).annotate(
                current_stock=Coalesce(
                    "current_stock_val",
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=15, decimal_places=2),
                )
            )
            inst = get_object_or_404(qs, pk=subp_id, parent=parent)
            ser = SubProductSerializer(
                inst, context={"request": req, "parent_product": parent}
            )
            return Response(ser.data)

        return cached_get(request, prod_pk, subp_pk)

    # PUT / DELETE: obtenemos la instancia validada (solo activos)
    instance = get_object_or_404(Subproduct, pk=subp_pk, parent=parent, status=True)

    if request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "Sin permiso."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SubProductSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request, "parent_product": parent},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                updated = serializer.save(user=request.user)
                qty_change = serializer.validated_data.get("quantity_change")
                reason = serializer.validated_data.get("reason")
                if qty_change is not None:
                    stock_rec = SubproductStock.objects.select_for_update().get(
                        subproduct=updated, status=True
                    )
                    adjust_subproduct_stock(
                        subproduct_stock=stock_rec,
                        quantity_change=qty_change,
                        reason=reason,
                        user=request.user,
                    )
                sync_parent_product_stock(updated.parent, acting_user=request.user)
        except Exception as e:
            logger.error(f"Error actualizando subproducto {subp_pk}: {e}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Invalidar caché y emitir evento WebSocket
        invalidate_subproduct_cache()
        # También invalidar cache de producto padre porque puede cambiar stock/flags
        try:
            from apps.products.utils.cache_invalidation import invalidate_product_cache
            invalidate_product_cache()
        except Exception:
            pass
        data = SubProductSerializer(
            updated, context={"request": request, "parent_product": parent}
        ).data
        broadcast_crud_event(
            event_type="update",
            app="products",
            model="Subproduct",
            data=data
        )
        # Emitir update del Product padre para refrescar stock/has_subproducts
        try:
            from apps.products.api.serializers.product_serializer import ProductSerializer
            parent_ser = ProductSerializer(parent, context={"request": request}).data
            broadcast_crud_event(
                event_type="update",
                app="products",
                model="Product",
                data=parent_ser,
            )
        except Exception:
            pass
        return Response(data)

    if request.method == "DELETE":
        if not request.user.is_staff:
            return Response({"detail": "Sin permiso."}, status=status.HTTP_403_FORBIDDEN)

        try:
            instance.delete(user=request.user)
            sync_parent_product_stock(parent, acting_user=request.user)
        except Exception as e:
            logger.error(f"Error eliminando subproducto {subp_pk}: {e}")
            return Response({"detail": "Error interno al eliminar."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Invalidar caché y emitir evento WebSocket
        invalidate_subproduct_cache()
        try:
            from apps.products.utils.cache_invalidation import invalidate_product_cache
            invalidate_product_cache()
        except Exception:
            pass
        broadcast_crud_event(
            event_type="delete",
            app="products",
            model="Subproduct",
            data={"id": instance.id}
        )
        # Emitir update del Product padre por posible cambio de stock/has_subproducts
        try:
            from apps.products.api.serializers.product_serializer import ProductSerializer
            parent_ser = ProductSerializer(parent, context={"request": request}).data
            broadcast_crud_event(
                event_type="update",
                app="products",
                model="Product",
                data=parent_ser,
            )
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
