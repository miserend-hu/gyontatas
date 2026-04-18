from django.db.models import QuerySet

from managementtool.models import Device
from managementtool.repositories.device_repository import DeviceRepository


class DeviceService:
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository

    def list_devices(self) -> QuerySet[Device]:
        return self.device_repository.get_all()
