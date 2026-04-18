import logging
import struct
from datetime import datetime, timezone

from django.db.models import QuerySet

from managementtool.models import DeviceUpdate
from managementtool.repositories.device_repository import DeviceRepository
from managementtool.repositories.device_update_repository import DeviceUpdateRepository
from managementtool.services.miserend_service import MiserendService

logger = logging.getLogger(__name__)

_TYPE1_MIN_LENGTH = 36


class DeviceUpdateService:
    def __init__(
        self,
        update_repository: DeviceUpdateRepository,
        device_repository: DeviceRepository,
        miserend_service: MiserendService,
    ):
        self.update_repository = update_repository
        self.device_repository = device_repository
        self.miserend_service = miserend_service

    def process_coap_update(self, device_type: str, raw_payload: bytes) -> DeviceUpdate:
        if device_type == "type1":
            return self._process_type1(raw_payload)
        if device_type == "type2":
            raise NotImplementedError("Type2 payload format is not yet defined")
        raise ValueError(f"Unknown device type: {device_type!r}")

    def list_updates_by_device(self, device_id: int) -> QuerySet[DeviceUpdate]:
        return self.update_repository.list_by_device(device_id)

    def list_updates_by_location(self, location_id: int) -> QuerySet[DeviceUpdate]:
        return self.update_repository.list_by_location(location_id)

    def retrieve_latest_update_by_device(self, device_id: int) -> DeviceUpdate:
        return self.update_repository.retrieve_latest_by_device(device_id)

    def _process_type1(self, raw_payload: bytes) -> DeviceUpdate:
        if len(raw_payload) < _TYPE1_MIN_LENGTH:
            raise ValueError(
                f"Type1 payload too short: expected at least {_TYPE1_MIN_LENGTH} bytes, got {len(raw_payload)}"
            )

        imei = _packed_id(raw_payload, 0)
        imsi = _packed_id(raw_payload, 8)
        version_product = raw_payload[16]
        version_code = raw_payload[17]
        battery_mv = struct.unpack_from(">H", raw_payload, 18)[0]
        signal = raw_payload[20]
        interrupt_3 = raw_payload[26]
        input_3 = raw_payload[27]
        interrupt_1 = raw_payload[28]
        input_1 = raw_payload[29]
        interrupt_2 = raw_payload[30]
        input_2 = raw_payload[31]
        time_unix = struct.unpack_from(">I", raw_payload, 32)[0]

        device = self.device_repository.get_by_imei(imei)
        update = DeviceUpdate(
            device=device,
            location=device.location,
            device_type="type1",
            timestamp=datetime.fromtimestamp(time_unix, tz=timezone.utc),
            imei=imei,
            imsi=imsi,
            version_product=version_product,
            version_code=version_code,
            battery=battery_mv / 1000.0,
            signal=signal,
            interrupt_1=interrupt_1,
            interrupt_2=interrupt_2,
            interrupt_3=interrupt_3,
            input_1=input_1,
            input_2=input_2,
            input_3=input_3,
            confession=input_1 + input_2 + input_3,
        )
        self.update_repository.create(update)
        logger.info("Saved DeviceUpdate for device %s (type=type1)", device.imei)

        try:
            self.miserend_service.report_confession(
                device,
                device.location,
                mode=1,
                door_status=1 if any(v == 1 for v in (input_1, input_2, input_3)) else 0,
                leak_status=None,
            )
        except Exception:
            logger.exception("miserend.hu report failed for device %s", device.imei)

        return update


def _packed_id(data: bytes, start: int) -> str:
    s = "".join(f"{b:02x}" for b in data[start : start + 8])
    if s[0].lower() == "f":
        s = s[1:]
    return s
