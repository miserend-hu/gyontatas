import json
from ipaddress import ip_address, ip_network

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from managementtool.coap_diagnostics import set_last_coap_message

_INTERNAL_NETWORKS = (
    ip_network("10.0.0.0/8"),
    ip_network("127.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
)


def _is_internal_request(request: HttpRequest) -> bool:
    remote_addr = request.META.get("REMOTE_ADDR")
    if not remote_addr:
        return False
    try:
        remote_ip = ip_address(remote_addr)
    except ValueError:
        return False
    return any(remote_ip in network for network in _INTERNAL_NETWORKS)


@csrf_exempt
@require_POST
def last_coap_message_view(request: HttpRequest) -> JsonResponse:
    if not _is_internal_request(request):
        return JsonResponse({"error": "Forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return JsonResponse({"error": f"Invalid JSON: {exc}"}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "Expected a JSON object."}, status=400)

    set_last_coap_message(payload)
    return JsonResponse({"ok": True})
