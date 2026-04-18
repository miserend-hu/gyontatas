from abc import ABC, abstractmethod


class PayloadProcessor(ABC):
    @abstractmethod
    def process(self, raw_payload: bytes) -> dict:
        """Parse raw CoAP payload bytes into a normalized DeviceUpdate field dict."""
