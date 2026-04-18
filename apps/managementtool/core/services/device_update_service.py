import logging

from django.db.models import QuerySet

from core.models import Device, DeviceUpdate
from core.processors.factory import PayloadProcessorFactory
from core.repositories.device_repository import DeviceRepository
from core.repositories.device_update_repository import DeviceUpdateRepository

logger = logging.getLogger(__name__)


class DeviceUpdateService:
    def __init__(
        self,
        update_repository: DeviceUpdateRepository,
        processor_factory: PayloadProcessorFactory,
        device_repository: DeviceRepository,
    ):
        self.update_repository = update_repository
        self.processor_factory = processor_factory
        self.device_repository = device_repository

    def process_coap_update(self, device_type: str, raw_payload: bytes) -> DeviceUpdate:
        processor = self.processor_factory.get_processor(device_type)
        data = processor.process(raw_payload)

        device = self._get_device(device_type, data)
        update = DeviceUpdate(
            device=device,
            location=device.location,
            device_type=data["device_type"],
            timestamp=data["timestamp"],
            imei=data.get("imei"),
            imsi=data.get("imsi"),
            version_product=data.get("version_product"),
            version_code=data.get("version_code"),
            battery=data.get("battery"),
            signal=data.get("signal"),
            interrupt_1=data.get("interrupt_1"),
            interrupt_2=data.get("interrupt_2"),
            interrupt_3=data.get("interrupt_3"),
            input_1=data.get("input_1"),
            input_2=data.get("input_2"),
            input_3=data.get("input_3"),
            confession=data.get("confession"),
        )
        self.update_repository.create(update)
        logger.info("Saved DeviceUpdate for device %s (type=%s)", device.imei, device_type)
        return update

    def list_updates_by_device(self, device_id: int) -> QuerySet[DeviceUpdate]:
        return self.update_repository.list_by_device(device_id)

    def list_updates_by_location(self, location_id: int) -> QuerySet[DeviceUpdate]:
        return self.update_repository.list_by_location(location_id)

    def retrieve_latest_update_by_device(self, device_id: int) -> DeviceUpdate:
        return self.update_repository.retrieve_latest_by_device(device_id)

    def _get_device(self, device_type: str, data: dict) -> Device:
        if device_type == "type1":
            return self.device_repository.get_by_imei(data["imei"])
        raise ValueError(f"Device lookup not implemented for device_type={device_type!r}")
