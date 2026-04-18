from django.views.generic import RedirectView


class RootRedirectView(RedirectView):
    permanent = False
    url = "/admin/"
