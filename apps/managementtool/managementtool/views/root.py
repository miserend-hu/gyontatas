import os
from django.views.generic import RedirectView


class RootRedirectView(RedirectView):
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        url_prefix = os.environ.get("URL_PREFIX", "").strip("/")
        if url_prefix:
            return f"/{url_prefix}/admin/"
        return "/admin/"
