"""Unit tests for intake JSON schema and fit rules."""

from __future__ import annotations

import json

import pytest

from src.errors import SchemaError
from src.schema import fit_requires_human, parse_intake, schema_instruction

VALID = {
    "summary": "Portal rebuild",
    "problem": "Legacy UI",
    "constraints": ["Discovery first"],
    "suggested_engagement": "product",
    "urgency": "medium",
    "confidence": 0.9,
    "open_questions": ["ERP vendor"],
}


def test_parse_valid() -> None:
    data = parse_intake(json.dumps(VALID))
    assert data["confidence"] == 0.9
    assert data["suggested_engagement"] == "product"


def test_parse_invalid_json() -> None:
    with pytest.raises(SchemaError, match="not valid JSON"):
        parse_intake("not json")


def test_parse_non_object() -> None:
    with pytest.raises(SchemaError, match="JSON object"):
        parse_intake("[1]")


def test_parse_missing_fields() -> None:
    with pytest.raises(SchemaError, match="Missing"):
        parse_intake("{}")


def test_parse_bad_engagement() -> None:
    payload = {**VALID, "suggested_engagement": "retainer"}
    with pytest.raises(SchemaError, match="suggested_engagement"):
        parse_intake(json.dumps(payload))


def test_parse_bad_urgency() -> None:
    payload = {**VALID, "urgency": "whenever"}
    with pytest.raises(SchemaError, match="urgency"):
        parse_intake(json.dumps(payload))


def test_parse_constraints_must_be_lists() -> None:
    payload = {**VALID, "constraints": "none"}
    with pytest.raises(SchemaError, match="lists"):
        parse_intake(json.dumps(payload))


def test_parse_confidence_must_be_number() -> None:
    payload = {**VALID, "confidence": "high"}
    with pytest.raises(SchemaError, match="confidence"):
        parse_intake(json.dumps(payload))


def test_fit_unknown() -> None:
    assert fit_requires_human({**VALID, "suggested_engagement": "unknown"})


def test_fit_low_confidence() -> None:
    assert fit_requires_human({**VALID, "confidence": 0.2})


def test_fit_pass() -> None:
    assert fit_requires_human(VALID) is None


def test_schema_instruction_mentions_keys() -> None:
    text = schema_instruction()
    assert "suggested_engagement" in text
    assert "confidence" in text
