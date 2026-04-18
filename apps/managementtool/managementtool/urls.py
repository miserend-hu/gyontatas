from django.contrib import admin
from django.urls import include, path

from core.views.root import RootRedirectView

urlpatterns = [
    path("", RootRedirectView.as_view()),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
]
