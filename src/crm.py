"""Illustrative CRM write. No live HubSpot — see docs/deployment.md."""

from __future__ import annotations

from typing import Any


def record_intake(lead_id: str, intake: dict[str, Any] | None, decision: str | None) -> None:
    """Would upsert a deal/activity in CRM. Intentionally a no-op stub."""
    _ = (lead_id, intake, decision)
    return None
