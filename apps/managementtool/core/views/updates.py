from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from core.models import DeviceUpdate
from core.processors.factory import PayloadProcessorFactory
from core.repositories.device_repository import DeviceRepository
from core.repositories.device_update_repository import DeviceUpdateRepository
from core.serializers import DeviceUpdateSerializer
from core.services.device_update_service import DeviceUpdateService


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
