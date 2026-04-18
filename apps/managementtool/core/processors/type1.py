import json
from datetime import datetime, timezone

from core.processors.base import PayloadProcessor


class Type1PayloadProcessor(PayloadProcessor):
    def process(self, raw_payload: bytes) -> dict:
        data = json.loads(raw_payload)
        return {
            "device_type": "type1",
            "imei": str(data["IMEI"]),
            "imsi": str(data["IMSI"]),
            "version_product": int(data["version_product"]),
            "version_code": int(data["version_code"]),
            "battery": int(data["battery"]),
            "signal": int(data["signal"]),
            "interrupt_1": int(data["interrupt_1"]),
            "interrupt_2": int(data["interrupt_2"]),
            "interrupt_3": int(data["interrupt_3"]),
            "input_1": int(data["input_1"]),
            "input_2": int(data["input_2"]),
            "input_3": int(data["input_3"]),
            "confession": int(data["confession"]),
            "timestamp": datetime.fromtimestamp(int(data["time"]), tz=timezone.utc),
        }
