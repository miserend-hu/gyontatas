from django.contrib import admin
from django.urls import include, path

from core.views.root import RootRedirectView

admin.site.site_header = "Management Tool"
admin.site.site_title = "Management Tool"
admin.site.index_title = "Management Tool"

urlpatterns = [
    path("", RootRedirectView.as_view()),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
]
