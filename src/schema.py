"""Structured intake JSON expected from the synthesize step."""

from __future__ import annotations

import json
from typing import Any

from src.errors import SchemaError

REQUIRED_FIELDS = (
    "summary",
    "problem",
    "constraints",
    "suggested_engagement",
    "urgency",
    "confidence",
    "open_questions",
)
ENGAGEMENTS = ("product", "staff_aug", "unknown")
URGENCIES = ("low", "medium", "high")
CONFIDENCE_THRESHOLD = 0.7


def fit_requires_human(intake: dict[str, Any]) -> str | None:
    """Illustrative fit rules — not official Taller policy."""
    if intake["suggested_engagement"] == "unknown":
        return "suggested_engagement is unknown"
    if intake["confidence"] < CONFIDENCE_THRESHOLD:
        return f"confidence {intake['confidence']} < {CONFIDENCE_THRESHOLD}"
    return None


def parse_intake(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SchemaError("Model output is not valid JSON") from exc
    if not isinstance(data, dict):
        raise SchemaError("Model output must be a JSON object")
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise SchemaError(f"Missing required fields: {missing}")
    if data["suggested_engagement"] not in ENGAGEMENTS:
        raise SchemaError(
            f"suggested_engagement must be one of {ENGAGEMENTS}"
        )
    if data["urgency"] not in URGENCIES:
        raise SchemaError(f"urgency must be one of {URGENCIES}")
    if not isinstance(data["constraints"], list) or not isinstance(
        data["open_questions"], list
    ):
        raise SchemaError("constraints and open_questions must be lists")
    try:
        data["confidence"] = float(data["confidence"])
    except (TypeError, ValueError) as exc:
        raise SchemaError("confidence must be a number") from exc
    return data


def schema_instruction() -> str:
    return (
        "Return ONLY a JSON object with keys: "
        "summary (string), problem (string), constraints (array of strings), "
        "suggested_engagement (product|staff_aug|unknown), "
        "urgency (low|medium|high), confidence (number 0-1), "
        "open_questions (array of strings). No markdown."
    )
