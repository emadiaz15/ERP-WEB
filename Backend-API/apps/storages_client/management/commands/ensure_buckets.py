import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from botocore.exceptions import ClientError
from apps.storages_client.clients.minio_client import get_minio_client

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Verifica y crea (si faltan) los buckets necesarios: productos y perfiles"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Sólo muestra el estado, no crea nada')

    def handle(self, *args, **options):
        client = get_minio_client()
        dry_run = options['dry_run']

        buckets = {
            'products': getattr(settings, 'AWS_PRODUCT_BUCKET_NAME', None),
            'profiles': getattr(settings, 'AWS_PROFILE_BUCKET_NAME', None),
        }

        missing_vars = [k for k, v in buckets.items() if not v]
        if missing_vars:
            self.stderr.write(self.style.WARNING(f"Variables de entorno faltantes para buckets: {', '.join(missing_vars)}"))

        existing = set()
        try:
            response = client.list_buckets()
            for b in response.get('Buckets', []):
                existing.add(b['Name'])
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error listando buckets: {e}"))
            return

        created = []
        for logical, bucket_name in buckets.items():
            if not bucket_name:
                continue
            if bucket_name in existing:
                self.stdout.write(self.style.SUCCESS(f"✓ {logical}: existe '{bucket_name}'"))
                continue
            if dry_run:
                self.stdout.write(self.style.WARNING(f"DRY-RUN: faltaría crear bucket '{bucket_name}' ({logical})"))
                continue
            try:
                client.create_bucket(Bucket=bucket_name)
                created.append(bucket_name)
                self.stdout.write(self.style.SUCCESS(f"+ Creado bucket '{bucket_name}' ({logical})"))
            except ClientError as ce:
                if ce.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    self.stdout.write(self.style.SUCCESS(f"✓ {logical}: '{bucket_name}' ya existe (race)"))
                else:
                    self.stderr.write(self.style.ERROR(f"✗ Error creando bucket '{bucket_name}': {ce}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"✗ Error inesperado creando bucket '{bucket_name}': {e}"))

        if not created:
            self.stdout.write(self.style.NOTICE("No se creó ningún bucket nuevo")) if hasattr(self.style, 'NOTICE') else self.stdout.write("No se creó ningún bucket nuevo")
        else:
            self.stdout.write(self.style.SUCCESS(f"Buckets creados: {', '.join(created)}"))

        self.stdout.write(self.style.SUCCESS("Finalizado ensure_buckets"))
