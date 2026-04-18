import logging

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from managementtool.models import DeviceUpdate
from managementtool.repositories.device_repository import DeviceRepository
from managementtool.repositories.device_update_repository import DeviceUpdateRepository
from managementtool.repositories.miserend_repository import MiserendRepository
from managementtool.serializers import DeviceUpdateSerializer
from managementtool.services.device_update_service import DeviceUpdateService
from managementtool.services.miserend_service import MiserendService

logger = logging.getLogger(__name__)


def _make_service() -> DeviceUpdateService:
    return DeviceUpdateService(
        DeviceUpdateRepository(),
        DeviceRepository(),
        MiserendService(MiserendRepository()),
    )


class LocationUpdateListView(ListAPIView):
    serializer_class = DeviceUpdateSerializer

    def get_queryset(self):
        return _make_service().list_updates_by_location(self.kwargs["location_id"])


class DeviceUpdateListView(ListAPIView):
    serializer_class = DeviceUpdateSerializer

    def get_queryset(self):
        return _make_service().list_updates_by_device(self.kwargs["device_id"])


class DeviceUpdateLatestView(RetrieveAPIView):
    serializer_class = DeviceUpdateSerializer

    def get_object(self):
        return _make_service().retrieve_latest_update_by_device(self.kwargs["device_id"])

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except DeviceUpdate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CoapRelayView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, device_type):
        try:
            _make_service().process_coap_update(device_type, request.body)
        except Exception:
            logger.exception("CoAP relay processing failed for device_type=%s", device_type)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)
