# metrics/urls.py
from django.urls import path

from .views import ProductsWithFilesPercentage, MySQLReadOnlyHealth
from apps.metrics.api.views import MetricParameterListCreateView, MetricParameterDetailView

urlpatterns = [
    path('products/with-files-percentage/', ProductsWithFilesPercentage.as_view()),
    path('mysql/health/', MySQLReadOnlyHealth.as_view()),
    path('parameters/', MetricParameterListCreateView.as_view(), name='metric-parameter-list'),
    path('parameters/<int:parameter_id>/', MetricParameterDetailView.as_view(), name='metric-parameter-detail'),
]
