from django.urls import path

from core.views.updates import (
    CoapRelayView,
    DeviceUpdateLatestView,
    DeviceUpdateListView,
    LocationUpdateListView,
)

urlpatterns = [
    path("coap/<str:device_type>/", CoapRelayView.as_view(), name="coap-relay"),
    path(
        "locations/<int:location_id>/updates/",
        LocationUpdateListView.as_view(),
        name="location-updates-list",
    ),
    path(
        "devices/<int:device_id>/updates/",
        DeviceUpdateListView.as_view(),
        name="device-updates-list",
    ),
    path(
        "devices/<int:device_id>/updates/latest/",
        DeviceUpdateLatestView.as_view(),
        name="device-updates-latest",
    ),
]
