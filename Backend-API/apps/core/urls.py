from django.urls import path

from apps.core.views import dashboard_view, mysql_readonly_health_view, public_home_view
from apps.core.views_public import service_health_view

urlpatterns = [
    path('', public_home_view, name='home'),  # Página inicial (pública, sin autenticación)
    path('dashboard/', dashboard_view, name='dashboard'),  # Dashboard (autenticado)
    path('health/', service_health_view, name='service-health'),
    path('health/mysql-readonly/', mysql_readonly_health_view, name='mysql-readonly-health'),
]
