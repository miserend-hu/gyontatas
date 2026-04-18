from core.processors.base import PayloadProcessor


class Type2PayloadProcessor(PayloadProcessor):
    def process(self, raw_payload: bytes) -> dict:
        raise NotImplementedError("Type2 payload format is not yet defined")
