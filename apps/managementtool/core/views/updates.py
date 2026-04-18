import logging

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import DeviceUpdate
from core.processors.factory import PayloadProcessorFactory
from core.repositories.device_repository import DeviceRepository
from core.repositories.device_update_repository import DeviceUpdateRepository
from core.repositories.miserend_repository import MiserendRepository
from core.serializers import DeviceUpdateSerializer
from core.services.device_update_service import DeviceUpdateService
from core.services.miserend_service import MiserendService

logger = logging.getLogger(__name__)


def _make_service() -> DeviceUpdateService:
    return DeviceUpdateService(
        DeviceUpdateRepository(),
        PayloadProcessorFactory(),
        DeviceRepository(),
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
        update_service = DeviceUpdateService(
            DeviceUpdateRepository(),
            PayloadProcessorFactory(),
            DeviceRepository(),
        )
        try:
            update = update_service.process_coap_update(device_type, request.body)
        except Exception:
            logger.exception("CoAP relay processing failed for device_type=%s", device_type)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if device_type == "type1" and update.input_1 is not None:
            try:
                MiserendService(MiserendRepository()).report_confession(
                    update.device,
                    update.location,
                    mode=1,
                    door_status=update.input_1,
                    leak_status=None,
                )
            except Exception:
                logger.exception("miserend.hu report failed for device %s", update.device.imei)

        return Response(status=status.HTTP_204_NO_CONTENT)
