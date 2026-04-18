from django.db.models import QuerySet

from core.models import DeviceUpdate


class DeviceUpdateRepository:
    def create(self, update: DeviceUpdate) -> None:
        update.save()

    def list_by_device(self, device_id: int) -> QuerySet[DeviceUpdate]:
        return DeviceUpdate.objects.filter(device_id=device_id)

    def list_by_location(self, location_id: int) -> QuerySet[DeviceUpdate]:
        return DeviceUpdate.objects.filter(location_id=location_id)

    def retrieve_latest_by_device(self, device_id: int) -> DeviceUpdate:
        return DeviceUpdate.objects.filter(device_id=device_id).latest("timestamp")
