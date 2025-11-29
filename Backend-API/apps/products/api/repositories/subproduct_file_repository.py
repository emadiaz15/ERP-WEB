# apps/products/api/repositories/subproduct_file_repository.py

from typing import Optional
import os
import logging

from apps.products.models.subproduct_image_model import SubproductImage
from apps.products.models.subproduct_model import Subproduct

logger = logging.getLogger(__name__)


class ProductNotFound(Exception):
    """Se lanza cuando no existe el producto o subproducto esperado."""
    pass


class SubproductFileRepository:
    """
    Repositorio para archivos de Subproduct adaptado para MinIO/S3.
    Permite listar, crear y eliminar registros de SubproductImage.
    """

    # Normaliza la variable de entorno y asegura puntos en las extensiones.
    # Por defecto incluimos imágenes, PDF y videos comunes para alinear con el <input accept>.
    _ext_env = os.getenv(
        "ALLOWED_UPLOAD_EXTENSIONS",
        ".jpg,.jpeg,.png,.webp,.pdf,.mp4,.webm",
    )
    ALLOWED_EXTENSIONS = [
        e.strip().lower() if e.strip().startswith(".") else f".{e.strip().lower()}"
        for e in _ext_env.split(",")
        if e.strip()
    ]

    # -------------------- Queries --------------------

    @staticmethod
    def get_all_by_subproduct(subproduct_id: int):
        return (
            SubproductImage.objects
            .filter(subproduct_id=subproduct_id)
            .order_by("created_at")
        )

    @staticmethod
    def get_by_id(file_key: str) -> Optional[SubproductImage]:
        try:
            return SubproductImage.objects.get(key=file_key)
        except SubproductImage.DoesNotExist:
            return None

    @staticmethod
    def exists(subproduct_id: int, file_key: str) -> bool:
        found = SubproductImage.objects.filter(
            subproduct_id=subproduct_id,
            key=file_key,
        ).exists()
        if not found:
            logger.info(
                "🛑 NO EXISTE SubproductFile: key=%s, subproduct_id=%s",
                file_key, subproduct_id
            )
        return found

    # -------------------- Commands --------------------

    @staticmethod
    def delete(file_key: str) -> Optional[SubproductImage]:
        try:
            img = SubproductImage.objects.get(key=file_key)
            img.delete()
            return img
        except SubproductImage.DoesNotExist:
            return None

    @staticmethod
    def create(
        subproduct_id: int,
        key: str,
        url: str = "",
        name: str = "",
        mime_type: str = "",
        product_id: Optional[int] = None,
        set_as_technical_sheet: bool = False,
        user=None,  # opcional: para auditar el seteo de ficha técnica
    ) -> SubproductImage:
        """
        Crea el registro SubproductImage para un subproducto (sin filtrar por status)
        y opcionalmente setea 'technical_sheet_photo' del subproducto.

        Args:
            subproduct_id: ID del subproducto.
            key: S3/MinIO object key.
            url: URL (opcional; si tu storage resuelve por key, puede ir vacío).
            name: Nombre original de archivo (se usa para validar extensión si existe).
            mime_type: MIME reportado por el upload/presign.
            product_id: Para validar pertenencia al producto padre cuando se provee.
            set_as_technical_sheet: Si True, marca technical_sheet_photo con key/url.
            user: (Opcional) usuario que acciona, para auditar en BaseModel.save(user=...).

        Returns:
            SubproductImage creado.
        """
        # --- Validación de extensión ---
        ext = os.path.splitext(name or key)[-1].lower()
        if ext not in SubproductFileRepository.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Extensión de archivo no permitida: {ext}. "
                f"Permitidas: {SubproductFileRepository.ALLOWED_EXTENSIONS}"
            )

        # --- Recuperar subproducto ignorando status (upload post-creación) ---
        try:
            base_qs = Subproduct._base_manager
            subp = (
                base_qs.get(pk=subproduct_id, parent_id=product_id)
                if product_id is not None
                else base_qs.get(pk=subproduct_id)
            )
        except Subproduct.DoesNotExist:
            raise ValueError(
                f"Subproducto con ID {subproduct_id} no existe"
                + (f" o no pertenece al producto {product_id}." if product_id is not None else ".")
            )

        # --- Crear imagen ---
        img = SubproductImage.objects.create(
            subproduct=subp,
            key=key,
            url=url,
            name=name,
            mime_type=mime_type,
        )

        # --- (Opcional) Setear como ficha técnica ---
        if set_as_technical_sheet and hasattr(subp, "technical_sheet_photo"):
            try:
                value = key or url
                if value:
                    subp.technical_sheet_photo = value
                    # Intentar auditar con user; si el modelo no acepta 'user', fallback.
                    try:
                        subp.save(user=user, update_fields=["technical_sheet_photo", "modified_at", "modified_by"])
                    except TypeError:
                        subp.save(update_fields=["technical_sheet_photo"])
            except Exception as e:
                logger.warning(
                    "No se pudo setear technical_sheet_photo para subproduct %s: %s",
                    subp.pk, e
                )

        return img
