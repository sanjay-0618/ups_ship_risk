"""Shared application state to avoid circular imports."""
from typing import Any

app_state: dict[str, Any] = {}

def get_state() -> dict[str, Any]:
    return app_state

