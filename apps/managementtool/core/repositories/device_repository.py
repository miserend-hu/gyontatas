from django.db.models import QuerySet

from core.models import Device


class DeviceRepository:
    def get_all(self) -> QuerySet[Device]:
        return Device.objects.all()

    def get_by_id(self, device_id: int) -> Device:
        return Device.objects.get(pk=device_id)

    def get_by_location(self, location_id: int) -> QuerySet[Device]:
        return Device.objects.filter(location_id=location_id)

    def get_by_imei(self, imei: str) -> Device:
        return Device.objects.get(imei=imei)
