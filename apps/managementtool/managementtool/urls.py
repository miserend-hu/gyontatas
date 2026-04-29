import os
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView

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

# Get URL prefix from environment
URL_PREFIX = os.environ.get("URL_PREFIX", "").strip("/")

# Define the app patterns
app_patterns = [
    path("", RootRedirectView.as_view()),
    re_path(r"^admin/core/(?P<rest>.*)$", RedirectView.as_view(url="/admin/managementtool/%(rest)s", permanent=True)),
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

# Apply prefix if set
if URL_PREFIX:
    urlpatterns = [
        path(f"{URL_PREFIX}/", include(app_patterns)),
    ]
else:
    urlpatterns = app_patterns
