# apps/cuts/api/urls.py
from django.urls import path
from apps.cuts.api.views.cutting_view import (
    cutting_order_list,
    cutting_order_assigned_list,
    cutting_order_create,
    cutting_order_detail,
    cutting_order_cancel,
)

urlpatterns = [
    # Lista todas las órdenes de corte activas
    path('cutting-orders/', cutting_order_list, name='cutting_orders_list'),

    # Lista solo las órdenes asignadas al usuario autenticado
    path('cutting-orders/assigned/', cutting_order_assigned_list, name='cutting_orders_assigned'),

    # Crea una nueva orden de corte
    path('cutting-orders/create/', cutting_order_create, name='cutting_order_create'),

    # Detalle, actualización y soft‑delete
    path('cutting-orders/<int:cuts_pk>/', cutting_order_detail, name='cutting_order_detail'),

    # Cancelar una orden (resta la reserva lógica al cambiar el estado)
    path('cutting-orders/<int:cuts_pk>/cancel/', cutting_order_cancel, name='cutting_order_cancel'),
]
