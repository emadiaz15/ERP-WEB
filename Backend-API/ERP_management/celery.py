# ERP_management/celery.py
import os
from celery import Celery

# Carga settings de Django. 
# Usa local como fallback si DJANGO_SETTINGS_MODULE no está definido.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ERP_management.settings.local")

app = Celery("ERP_management")

# Toma todas las variables que empiecen con CELERY_ desde settings de Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre automáticamente tasks.py en todas las apps instaladas
app.autodiscover_tasks()
