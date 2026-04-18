import uuid
from datetime import datetime, timezone

from core.models import Device, Location
from core.repositories.miserend_repository import MiserendLorawanPayload, MiserendRepository


class MiserendService:
    def __init__(self, miserend_repository: MiserendRepository):
        self.miserend_repository = miserend_repository

    def report_confession(
        self,
        device: Device,
        location: Location,
        mode: int,
        door_status: int | None,
        leak_status: int | None,
    ) -> None:
        now = datetime.now(tz=timezone.utc)
        time_str = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}+00:00"

        # devEui: 16 hex chars derived from serial_number (IMEI zero-padded)
        dev_eui = device.serial_number.zfill(16)[:16].lower()

        payload = MiserendLorawanPayload(
            deduplication_id=str(uuid.uuid4()),
            time=time_str,
            dev_eui=dev_eui,
            templom_id=location.miserend_id,
            local_id=device.id,
            mode=mode,
            door_status=door_status,
            leak_status=leak_status,
        )
        self.miserend_repository.report_confession(payload)
