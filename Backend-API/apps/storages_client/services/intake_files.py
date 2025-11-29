import io
import os
import uuid
import logging
import requests
from mimetypes import guess_type
from django.conf import settings
from apps.storages_client.clients.minio_client import get_minio_client
from apps.storages_client.services.s3_file_access import generate_presigned_url

logger = logging.getLogger(__name__)

ALLOWED = set((os.getenv("ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.webp,.pdf").split(",")))


def _validate_ext(name: str):
    ext = os.path.splitext(name.lower())[1]
    if ext not in ALLOWED:
        raise ValueError(f"Extensión no permitida: {ext}. Permitidas: {sorted(ALLOWED)}")
    return ext


def upload_intake_file(fileobj, filename: str, conversation_id: str | None = None) -> dict:
    """
    Sube un archivo (file-like) al bucket de intake.
    Genera una key única y devuelve {key, url, content_type, name}
    """
    ext = _validate_ext(filename or "upload.bin")
    uid = uuid.uuid4().hex
    base = f"intake/{conversation_id or 'generic'}/{uid}{ext}"
    s3 = get_minio_client()

    content_type, _ = guess_type(filename or "")
    if not content_type:
        content_type = "application/octet-stream"

    fileobj.seek(0)
    s3.upload_fileobj(
        Fileobj=fileobj,
        Bucket=settings.AWS_INTAKE_BUCKET_NAME,
        Key=base,
        ExtraArgs={"ContentType": content_type},
    )
    url = generate_presigned_url(bucket=settings.AWS_INTAKE_BUCKET_NAME, object_name=base)
    return {"key": base, "url": url, "content_type": content_type, "name": filename}


def upload_intake_from_url(url: str, filename: str | None = None, conversation_id: str | None = None, timeout=30) -> dict:
    """
    Descarga en streaming una URL remota (por ej. media de WhatsApp) y la sube al bucket intake.
    """
    if not filename:
        try:
            filename = url.split("?")[0].split("/")[-1] or "upload.jpg"
        except Exception:
            filename = "upload.jpg"

    _ = _validate_ext(filename)

    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        chunked = io.BytesIO(r.content)
        return upload_intake_file(chunked, filename=filename, conversation_id=conversation_id)
