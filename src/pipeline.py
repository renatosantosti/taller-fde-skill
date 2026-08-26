"""Orchestration stub: deterministic gates around an LLM judgment step.

This is not a company workflow. It is the integration pattern the assignment
asks for: classify work, call a model only where judgment is required, and
fail closed to a human on timeout, bad schema, refusal, or low confidence.

Replace the NotImplementedError helpers after the workflow is chosen.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from src.errors import (
    LlmTimeoutError,
    LowConfidenceError,
    NeedsHumanError,
    PolicyError,
    SchemaError,
)


# Steps that are rules belong here, not in a prompt.
DETERMINISTIC_REQUIRED_FIELDS = ("id", "payload")


@dataclass(frozen=True)
class PipelineResult:
    status: str  # "ok" | "needs_human"
    data: dict[str, Any] | None
    human_reason: str | None = None


def validate_input(event: dict[str, Any]) -> dict[str, Any]:
    """Deterministic: reject malformed events before any model call."""
    missing = [field for field in DETERMINISTIC_REQUIRED_FIELDS if field not in event]
    if missing:
        raise NeedsHumanError(
            f"Input missing required fields: {missing}. Not an LLM problem."
        )
    return event


def call_llm(event: dict[str, Any]) -> str:
    """LLM judgment: non-deterministic step. Not implemented in the scaffold."""
    raise NotImplementedError(
        "TODO: call the model for the chosen workflow step. "
        "Must surface timeout, policy refusal, and raw text for schema parse."
    )


def parse_and_validate_output(raw: str) -> dict[str, Any]:
    """Deterministic: structured output or schema failure (never 'best effort')."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SchemaError("Model output is not valid JSON") from exc
    if not isinstance(data, dict):
        raise SchemaError("Model output must be a JSON object")
    return data


def confidence_ok(data: dict[str, Any], *, threshold: float = 0.7) -> None:
    """Deterministic gate on a model-provided confidence field, if present."""
    confidence = data.get("confidence")
    if confidence is None:
        return
    try:
        value = float(confidence)
    except (TypeError, ValueError) as exc:
        raise SchemaError("confidence must be a number") from exc
    if value < threshold:
        raise LowConfidenceError(f"confidence {value} < {threshold}")


def run(event: dict[str, Any]) -> PipelineResult:
    """One pipeline pass.

    Happy path returns status "ok". Every anticipated LLM failure becomes
    status "needs_human" — fail closed, no side effects.
    """
    try:
        validated = validate_input(event)
        raw = call_llm(validated)
        data = parse_and_validate_output(raw)
        confidence_ok(data)
        return PipelineResult(status="ok", data=data)
    except NotImplementedError:
        raise
    except LlmTimeoutError as exc:
        raise NeedsHumanError("LLM timeout", cause=exc) from exc
    except SchemaError as exc:
        raise NeedsHumanError("Invalid model output schema", cause=exc) from exc
    except PolicyError as exc:
        raise NeedsHumanError("Policy or model refusal", cause=exc) from exc
    except LowConfidenceError as exc:
        raise NeedsHumanError("Low confidence", cause=exc) from exc
    except NeedsHumanError:
        raise


def main() -> None:
    sample = {"id": "scaffold", "payload": {"text": "TODO: real event"}}
    try:
        result = run(sample)
    except NotImplementedError as exc:
        print(f"scaffold: {exc}")
        return
    except NeedsHumanError as exc:
        print(f"needs_human: {exc.reason}")
        return
    print(result)


if __name__ == "__main__":
    main()
