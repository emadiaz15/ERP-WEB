from django.urls import path
from apps.notifications.api.views.notification_views import (
    my_notifications_list,
    my_notification_detail,
    my_notifications_summary,
    mark_notification_read,
    mark_all_notifications_read,
    notification_cache_metrics,
)

urlpatterns = [
    path("", my_notifications_list, name="my_notifications_list"),
    path("<int:notif_pk>/", my_notification_detail, name="my_notification_detail"),
    path("summary/", my_notifications_summary, name="my_notifications_summary"),
    path("cache-metrics/", notification_cache_metrics, name="notification_cache_metrics"),
    path("<int:notif_pk>/read/", mark_notification_read, name="mark_notification_read"),
    path("mark-all-read/", mark_all_notifications_read, name="mark_all_notifications_read"),
]
