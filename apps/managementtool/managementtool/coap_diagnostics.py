from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any

_lock = Lock()
_last_message: dict[str, Any] | None = None


def set_last_coap_message(message: dict[str, Any]) -> None:
    global _last_message
    with _lock:
        _last_message = {
            "stored_at": datetime.now(timezone.utc).isoformat(),
            **message,
        }


def get_last_coap_message() -> dict[str, Any] | None:
    with _lock:
        return dict(_last_message) if _last_message is not None else None
