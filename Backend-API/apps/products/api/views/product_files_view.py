# apps/products/api/views/product_files_view.py

import logging
from django.http import HttpResponseRedirect, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_spectacular.utils import extend_schema

from apps.products.models import Product
from apps.products.api.repositories.product_file_repository import (
    ProductFileRepository,
    ProductNotFound,
)
from apps.storages_client.services.products_files import (
    upload_product_file,
    delete_product_file,
    get_product_file_url,
)
from apps.products.docs.product_image_doc import (
    product_image_upload_doc,
    product_image_list_doc,
    product_image_download_doc,
    product_image_delete_doc,
)
from apps.products.utils.cache_invalidation import invalidate_product_cache
from apps.core.utils import broadcast_crud_event

logger = logging.getLogger(__name__)


@extend_schema(
    tags=product_image_upload_doc["tags"],
    summary=product_image_upload_doc["summary"],
    operation_id=product_image_upload_doc["operation_id"],
    description=product_image_upload_doc["description"],
    parameters=product_image_upload_doc["parameters"],
    request=product_image_upload_doc["requestBody"]["content"]["multipart/form-data"]["schema"],
    responses=product_image_upload_doc["responses"],
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def product_file_upload_view(request, product_id: str):
    """
    Sube archivos para un producto; invalida caché de lista y detalle.
    """
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")

    files = request.FILES.getlist("file")
    if not files:
        return Response({"detail": "No se proporcionaron archivos."}, status=status.HTTP_400_BAD_REQUEST)

    results, errors = [], []
    for f in files:
        try:
            res = upload_product_file(file=f, product_id=str(product.id))
            ProductFileRepository.create(
                product_id=product.id,
                key=res["key"],
                url=res["url"],
                name=res["name"],
                mime_type=res["mimeType"],
            )
            results.append(res["key"])
        except Exception as e:
            logger.exception(f"❌ Error subiendo archivo {f.name}: {e}")
            errors.append({f.name: str(e)})

    if results:
        # Invalidar caché de lista y detalle y emitir evento WebSocket
        invalidate_product_cache()
        logger.debug("[Cache] product_list y product_detail invalidada tras UPLOAD")
        broadcast_crud_event(
            event_type="create",
            app="products",
            model="ProductFile",
            data={"product_id": product_id, "files": results}
        )

    if errors and not results:
        only_ext_errors = all("Extensión de archivo no permitida" in list(err.values())[0] for err in errors)
        code = status.HTTP_400_BAD_REQUEST if only_ext_errors else status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Archivos inválidos." if only_ext_errors else "Ningún archivo pudo subirse."
        return Response({"detail": detail, "errors": errors}, status=code)

    return Response(
        {"uploaded": results, "errors": errors or None},
        status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
    )


@extend_schema(
    tags=product_image_list_doc["tags"],
    summary=product_image_list_doc["summary"],
    operation_id=product_image_list_doc["operation_id"],
    description=product_image_list_doc["description"],
    parameters=product_image_list_doc["parameters"],
    responses=product_image_list_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_file_list_view(request, product_id: str):
    try:
        Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        files = ProductFileRepository.get_all_by_product(product_id)
        return Response({"files": files}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error listando archivos de producto {product_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=product_image_download_doc["tags"],
    summary=product_image_download_doc["summary"],
    operation_id=product_image_download_doc["operation_id"],
    description=product_image_download_doc["description"],
    parameters=product_image_download_doc["parameters"],
    responses=product_image_download_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_file_download_view(request, product_id: str, file_id: str):
    try:
        Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    if not ProductFileRepository.exists(product_id, file_id):
        raise Http404("Archivo no vinculado al producto.")
    try:
        url = get_product_file_url(file_id)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.exception(f"❌ Error generando URL para {file_id}: {e}")
        return Response({"detail": "Error generando acceso al archivo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=product_image_delete_doc["tags"],
    summary=product_image_delete_doc["summary"],
    operation_id=product_image_delete_doc["operation_id"],
    description=product_image_delete_doc["description"],
    parameters=product_image_delete_doc["parameters"],
    responses=product_image_delete_doc["responses"],
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def product_file_delete_view(request, product_id: str, file_id: str):
    try:
        Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    if not ProductFileRepository.exists(product_id, file_id):
        return Response({"detail": "Archivo no vinculado al producto."}, status=status.HTTP_404_NOT_FOUND)
    try:
        delete_product_file(file_id)
        ProductFileRepository.delete(file_id)
        # Invalidar caché de lista y detalle y emitir evento WebSocket
        invalidate_product_cache()
        logger.debug("[Cache] product_list y product_detail invalidada tras DELETE")
        broadcast_crud_event(
            event_type="delete",
            app="products",
            model="ProductFile",
            data={"product_id": product_id, "file_id": file_id}
        )
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error eliminando archivo {file_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Shim para tests que hacen patch sobre get_redis_connection ---
try:
    # Pylance puede no resolver este import en tu host; en runtime funciona.
    from django_redis import get_redis_connection as _dr_get_redis_connection  # type: ignore
except Exception:  # pragma: no cover
    _dr_get_redis_connection = None


def get_redis_connection(alias="default"):
    """
    Shim de compatibilidad para tests.
    Permite que unittest.mock.patch(...) encuentre el símbolo en este módulo.
    """
    if _dr_get_redis_connection is None:
        # Fallback: devolvemos None para que el patch del test reemplace el valor
        return None
    return _dr_get_redis_connection(alias)
# ------------------------------------------------------------------


@extend_schema(
    tags=["Public"],
    summary="Listado público de archivos por código de producto",
    description=(
        "Devuelve los metadatos básicos del producto y la lista de archivos "
        "disponibles para el código proporcionado. El acceso no requiere autenticación."
    ),
    parameters=[
        {
            "name": "code",
            "in": "query",
            "required": True,
            "description": "Código del producto a consultar",
            "schema": {"type": "string"},
        }
    ],
    responses={
        200: {"description": "Producto encontrado"},
        400: {"description": "Parámetro obligatorio ausente"},
        404: {"description": "Producto no encontrado"},
        500: {"description": "Fallo interno al procesar la solicitud"},
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def public_product_file_list_view(request):
    code = (request.query_params.get("code") or "").strip()
    if not code:
        return Response(
            {"detail": "El parámetro 'code' es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = (
        Product.objects.filter(code__iexact=code, status=True)
        .select_related("category")
        .first()
    )
    if not product:
        return Response(
            {"detail": "Producto no encontrado o inactivo."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        files = ProductFileRepository.get_all_by_product(product.id)
    except Exception as exc:  # pragma: no cover - logging path
        logger.exception(
            "❌ Error listando archivos públicos para el producto %s: %s",
            product.id,
            exc,
        )
        return Response(
            {"detail": "No fue posible obtener los archivos del producto."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    payload = {
        "product": {
            "id": product.id,
            "code": product.code,
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "location": product.location,
            "position": product.position,
            "has_subproducts": product.has_subproducts,
            "category": {
                "id": product.category_id,
                "name": product.category.name if product.category else None,
            },
        },
        "files": files,
    }

    response = Response(payload, status=status.HTTP_200_OK)
    response["Cache-Control"] = "public, max-age=300"
    return response
