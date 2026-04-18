import struct
from datetime import datetime, timezone

from managementtool.processors.base import PayloadProcessor

MIN_LENGTH = 36


class Type1PayloadProcessor(PayloadProcessor):
    def process(self, raw_payload: bytes) -> dict:
        if len(raw_payload) < MIN_LENGTH:
            raise ValueError(
                f"Type1 payload too short: expected at least {MIN_LENGTH} bytes, got {len(raw_payload)}"
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

        return {
            "device_type": "type1",
            "imei": imei,
            "imsi": imsi,
            "version_product": version_product,
            "version_code": version_code,
            "battery": battery_mv / 1000.0,
            "signal": signal,
            "interrupt_1": interrupt_1,
            "interrupt_2": interrupt_2,
            "interrupt_3": interrupt_3,
            "input_1": input_1,
            "input_2": input_2,
            "input_3": input_3,
            "confession": input_1 + input_2 + input_3,
            "door_status": _door_status(input_1, input_2, input_3),
            "timestamp": datetime.fromtimestamp(time_unix, tz=timezone.utc),
        }


def _door_status(input_1: int, input_2: int, input_3: int) -> int:
    return 1 if any(v == 1 for v in (input_1, input_2, input_3)) else 0


def _packed_id(data: bytes, start: int) -> str:
    s = "".join(f"{b:02x}" for b in data[start : start + 8])
    if s[0].lower() == "f":
        s = s[1:]
    return s
