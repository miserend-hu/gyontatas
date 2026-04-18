from django.contrib import admin
from django.urls import path

from managementtool.views.root import RootRedirectView
from managementtool.views.updates import (
    CoapRelayView,
    DeviceUpdateLatestView,
    DeviceUpdateListView,
    LocationUpdateListView,
)

admin.site.site_header = "Management Tool"
admin.site.site_title = "Management Tool"
admin.site.index_title = "Management Tool"

urlpatterns = [
    path("", RootRedirectView.as_view()),
    path("admin/", admin.site.urls),
    path("api/coap/<str:device_type>/", CoapRelayView.as_view(), name="coap-relay"),
    path(
        "api/locations/<int:location_id>/updates/",
        LocationUpdateListView.as_view(),
        name="location-updates-list",
    ),
    path(
        "api/devices/<int:device_id>/updates/",
        DeviceUpdateListView.as_view(),
        name="device-updates-list",
    ),
    path(
        "api/devices/<int:device_id>/updates/latest/",
        DeviceUpdateLatestView.as_view(),
        name="device-updates-latest",
    ),
]
