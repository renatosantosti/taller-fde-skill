"""Bus port. FileBus stands in for Azure Service Bus (see adr005)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from src.paths import BUS_ROOT

TOPIC_REVIEW = "intake-needs-review"
TOPIC_DECISION = "intake-decisions"


@dataclass
class IntakeNeedsReview:
    lead_id: str
    reason: str
    intake: dict[str, Any] | None = None


@dataclass
class IntakeDecision:
    lead_id: str
    decision: str  # bid | decline | request_call
    notes: str = ""


class Bus(Protocol):
    def publish(self, topic: str, lead_id: str, payload: dict[str, Any]) -> Path: ...
    def get(self, topic: str, lead_id: str) -> dict[str, Any] | None: ...


class FileBus:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or BUS_ROOT

    def _path(self, topic: str, lead_id: str) -> Path:
        folder = self.root / topic
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{lead_id}.json"

    def publish(self, topic: str, lead_id: str, payload: dict[str, Any]) -> Path:
        path = self._path(topic, lead_id)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def get(self, topic: str, lead_id: str) -> dict[str, Any] | None:
        path = self._path(topic, lead_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


def review_payload(message: IntakeNeedsReview) -> dict[str, Any]:
    return asdict(message)


def decision_payload(message: IntakeDecision) -> dict[str, Any]:
    return asdict(message)
