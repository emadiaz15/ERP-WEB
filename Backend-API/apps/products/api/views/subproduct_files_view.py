# apps/products/api/views/subproduct_files_view.py

import logging
from django.http import HttpResponseRedirect, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema

from apps.products.models import Product, Subproduct
from apps.products.models.subproduct_image_model import SubproductImage
from apps.products.api.serializers.subproduct_image_serializer import SubproductImageSerializer
from apps.products.api.repositories.subproduct_file_repository import (
    SubproductFileRepository,
    ProductNotFound,
)
from apps.storages_client.services.subproducts_files import (
    upload_subproduct_file,
    delete_subproduct_file,
    get_subproduct_file_url,
)
from apps.products.docs.subproduct_image_doc import (
    subproduct_image_upload_doc,
    subproduct_image_list_doc,
    subproduct_image_download_doc,
    subproduct_image_delete_doc,
)
from apps.products.utils.cache_invalidation import invalidate_subproduct_cache
from apps.core.utils import broadcast_crud_event

logger = logging.getLogger(__name__)

# ========== Helpers ===========================================================

def _get_parent_and_subproduct_or_404(product_id: str, subproduct_id: str):
    try:
        product = Product.objects.get(pk=product_id, status=True)
    except Product.DoesNotExist:
        raise ProductNotFound(f"Producto con ID {product_id} no existe.")
    try:
        # Usar _base_manager para no filtrar por status en endpoints de archivos
        subproduct = Subproduct._base_manager.get(pk=subproduct_id, parent_id=product.id)
    except Subproduct.DoesNotExist:
        raise Http404(f"Subproducto con ID {subproduct_id} no existe para el producto {product_id}.")
    return product, subproduct


def _resolve_file_key_for_subproduct(subproduct_id: int, file_id: str) -> str | None:
    """
    Acepta key (string) o id numérico y devuelve siempre la key (string) si
    está vinculada al subproducto.
    """
    # ¿Ya es la key?
    if SubproductFileRepository.exists(subproduct_id=subproduct_id, file_key=file_id):
        return file_id

    # ¿Es un id numérico?
    if str(file_id).isdigit():
        try:
            img = SubproductImage.objects.get(id=int(file_id), subproduct_id=subproduct_id)
            return img.key
        except SubproductImage.DoesNotExist:
            return None

    return None


# ========== Upload ============================================================

@extend_schema(
    tags=subproduct_image_upload_doc["tags"],
    summary=subproduct_image_upload_doc["summary"],
    operation_id=subproduct_image_upload_doc["operation_id"],
    description=subproduct_image_upload_doc["description"],
    parameters=subproduct_image_upload_doc["parameters"],
    request=subproduct_image_upload_doc["request"]["content"]["multipart/form-data"]["schema"],
    responses=subproduct_image_upload_doc["responses"],
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def subproduct_file_upload_view(request, product_id: str, subproduct_id: str):
    """
    Sube uno o varios archivos para un subproducto.
    Invalida caché de lista y detalle tras una subida exitosa.
    """
    product, subproduct = _get_parent_and_subproduct_or_404(product_id, subproduct_id)

    files = request.FILES.getlist("file")
    if not files:
        return Response({"detail": "No se proporcionaron archivos."}, status=status.HTTP_400_BAD_REQUEST)

    # Flag opcional para marcar como 'ficha técnica'
    raw_flag = (request.data.get("set_as_technical_sheet") or "").strip().lower()
    set_as_technical_sheet = raw_flag in {"1", "true", "yes", "on"}

    results, errors = [], []
    for f in files:
        try:
            res = upload_subproduct_file(
                file=f,
                product_id=product.id,     # asegurar pk real
                subproduct_id=subproduct.id
            )
            SubproductFileRepository.create(
                subproduct_id=subproduct.id,
                key=res["key"],
                url=res.get("url", ""),
                name=res.get("name", res["key"]),
                mime_type=res.get("mimeType", ""),  # normalizado a campo del modelo
                product_id=product.id,
                set_as_technical_sheet=set_as_technical_sheet,
            )
            results.append(res["key"])
        except Exception as e:
            logger.exception(f"❌ Error subiendo archivo {getattr(f,'name', 'file')}: {e}")
            errors.append({getattr(f, 'name', 'file'): str(e)})

    # Invalidar caché si hubo subidas exitosas
    if results:
        invalidate_subproduct_cache()
        logger.debug("[Cache] subproduct_list y subproduct_detail invalidada tras UPLOAD")
        broadcast_crud_event(
            event_type="create",
            app="products",
            model="SubproductFile",
            data={"product_id": product_id, "subproduct_id": subproduct_id, "files": results}
        )

    # Si todos fallaron
    if errors and not results:
        only_ext_errors = all("Extensión de archivo no permitida" in list(err.values())[0] for err in errors)
        status_code = status.HTTP_400_BAD_REQUEST if only_ext_errors else status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Archivos inválidos." if only_ext_errors else "Ningún archivo pudo subirse."
        return Response({"detail": detail, "errors": errors}, status=status_code)

    return Response(
        {"uploaded": results, "errors": errors or None},
        status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED
    )


# ========== List ==============================================================

@extend_schema(
    tags=subproduct_image_list_doc["tags"],
    summary=subproduct_image_list_doc["summary"],
    operation_id=subproduct_image_list_doc["operation_id"],
    description=subproduct_image_list_doc["description"],
    parameters=subproduct_image_list_doc["parameters"],
    responses=subproduct_image_list_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_list_view(request, product_id: str, subproduct_id: str):
    """
    Lista archivos de un subproducto (serializados).
    """
    _, subproduct = _get_parent_and_subproduct_or_404(product_id, subproduct_id)

    try:
        qs = SubproductFileRepository.get_all_by_subproduct(subproduct.id)
        data = SubproductImageSerializer(qs, many=True).data
        return Response({"files": data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error listando archivos de subproducto {subproduct_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== Download (redirect) ==============================================

@extend_schema(
    tags=subproduct_image_download_doc["tags"],
    summary=subproduct_image_download_doc["summary"],
    operation_id=subproduct_image_download_doc["operation_id"],
    description=subproduct_image_download_doc["description"],
    parameters=subproduct_image_download_doc["parameters"],
    responses=subproduct_image_download_doc["responses"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_download_view(request, product_id: str, subproduct_id: str, file_id: str):
    """
    Redirige a la URL presignada de un archivo de subproducto.
    Acepta key o id numérico.
    """
    _, subproduct = _get_parent_and_subproduct_or_404(product_id, subproduct_id)

    key = _resolve_file_key_for_subproduct(subproduct.id, file_id)
    if not key:
        raise Http404(f"Archivo {file_id} no está vinculado al subproducto {subproduct_id}.")

    try:
        url = get_subproduct_file_url(key)
        return HttpResponseRedirect(url)
    except Exception as e:
        logger.exception(f"❌ Error generando URL presignada para archivo {file_id}: {e}")
        return Response({"detail": "Error generando acceso al archivo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== Presign (JSON) ====================================================

@extend_schema(
    tags=subproduct_image_download_doc["tags"],
    summary="Obtiene URL presignada (JSON) para un archivo de subproducto",
    operation_id="subproduct-file-presign",
    description="Devuelve { url: <presigned_url> } para usar directamente en <img>/<video>/<a>.",
    parameters=subproduct_image_download_doc["parameters"],
    responses={200: {"type": "object", "properties": {"url": {"type": "string"}}}},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subproduct_file_presign_view(request, product_id: str, subproduct_id: str, file_id: str):
    """
    Igual que download pero sin redirect. Acepta key o id numérico.
    """
    _, subproduct = _get_parent_and_subproduct_or_404(product_id, subproduct_id)

    key = _resolve_file_key_for_subproduct(subproduct.id, file_id)
    if not key:
        raise Http404(f"Archivo {file_id} no está vinculado al subproducto {subproduct_id}.")

    try:
        url = get_subproduct_file_url(key)
        return Response({"url": url}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error generando URL presignada para archivo {file_id}: {e}")
        return Response({"detail": "Error generando acceso al archivo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== Delete ============================================================

@extend_schema(
    tags=subproduct_image_delete_doc["tags"],
    summary=subproduct_image_delete_doc["summary"],
    operation_id=subproduct_image_delete_doc["operation_id"],
    description=subproduct_image_delete_doc["description"],
    parameters=subproduct_image_delete_doc["parameters"],
    responses=subproduct_image_delete_doc["responses"],
)
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def subproduct_file_delete_view(request, product_id: str, subproduct_id: str, file_id: str):
    """
    Elimina un archivo de subproducto y actualiza la caché de lista y detalle.
    Acepta key o id numérico.
    """
    _, subproduct = _get_parent_and_subproduct_or_404(product_id, subproduct_id)

    key = _resolve_file_key_for_subproduct(subproduct.id, file_id)
    if not key:
        return Response({"detail": "El archivo no está vinculado a este subproducto."},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        delete_subproduct_file(key)
        SubproductFileRepository.delete(key)
        invalidate_subproduct_cache()
        logger.debug("[Cache] subproduct_list y subproduct_detail invalidada tras DELETE")
        broadcast_crud_event(
            event_type="delete",
            app="products",
            model="SubproductFile",
            data={"product_id": product_id, "subproduct_id": subproduct_id, "file_id": file_id}
        )
        return Response({"detail": "Archivo eliminado correctamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"❌ Error eliminando archivo {file_id} de subproducto {subproduct_id}: {e}")
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
