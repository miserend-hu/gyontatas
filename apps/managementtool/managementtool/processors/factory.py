from managementtool.processors.base import PayloadProcessor
from managementtool.processors.type1 import Type1PayloadProcessor
from managementtool.processors.type2 import Type2PayloadProcessor


class PayloadProcessorFactory:
    def get_processor(self, device_type: str) -> PayloadProcessor:
        if device_type == "type1":
            return Type1PayloadProcessor()
        if device_type == "type2":
            return Type2PayloadProcessor()
        raise ValueError(f"Unknown device type: {device_type!r}")
