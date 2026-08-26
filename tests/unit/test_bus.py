"""Unit tests for the file-bus port."""

from __future__ import annotations

from pathlib import Path

from src.bus import (
    TOPIC_REVIEW,
    FileBus,
    IntakeDecision,
    IntakeNeedsReview,
    decision_payload,
    review_payload,
)


def test_publish_and_get(tmp_path: Path) -> None:
    bus = FileBus(tmp_path / "bus")
    bus.publish(TOPIC_REVIEW, "lead-x", {"lead_id": "lead-x", "reason": "test"})
    got = bus.get(TOPIC_REVIEW, "lead-x")
    assert got is not None
    assert got["reason"] == "test"


def test_get_missing(tmp_path: Path) -> None:
    bus = FileBus(tmp_path / "bus")
    assert bus.get(TOPIC_REVIEW, "missing") is None


def test_payload_helpers() -> None:
    review = review_payload(IntakeNeedsReview(lead_id="a", reason="thin", intake=None))
    assert review["lead_id"] == "a"
    decision = decision_payload(IntakeDecision(lead_id="a", decision="bid", notes="ok"))
    assert decision["decision"] == "bid"
    assert decision["notes"] == "ok"
