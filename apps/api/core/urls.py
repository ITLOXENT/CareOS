from django.urls import path

from . import views


urlpatterns = [
    path("health/", views.health),
    path("me/", views.me),
    path("orgs/current/", views.current_org),
    path("audit-events/", views.audit_events),
]
