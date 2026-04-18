from dataclasses import dataclass

import requests


@dataclass
class MiserendLorawanPayload:
    deduplication_id: str
    time: str
    dev_eui: str
    templom_id: int
    local_id: int
    mode: int
    door_status: int | None
    leak_status: int | None


class MiserendRepository:
    URL = "https://miserend.hu/api/v4/lorawan"

    def report_confession(self, payload: MiserendLorawanPayload) -> None:
        body = {
            "deduplicationId": payload.deduplication_id,
            "time": payload.time,
            "deviceInfo": {
                "devEui": payload.dev_eui,
                "tags": {
                    "templom_id": payload.templom_id,
                    "local_id": payload.local_id,
                },
            },
            "object": {
                "Mód": payload.mode,
            },
        }
        if payload.door_status is not None:
            body["object"]["Satus_Door"] = payload.door_status
        if payload.leak_status is not None:
            body["object"]["Status_Leak"] = payload.leak_status

        response = requests.post(self.URL, json=body, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("error") == 1:
            raise ValueError(f"miserend.hu error: {data.get('text', 'unknown error')}")
