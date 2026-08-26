"""Failure modes for LLM-backed steps.

Callers should map these to a human-in-the-loop queue, not to a side effect
(email, ticket, payment, write-back) unless a human has approved the result.
"""

from __future__ import annotations


class PipelineError(Exception):
    """Base error for the integration pipeline."""


class LlmTimeoutError(PipelineError):
    """The model or downstream system did not respond in time."""


class SchemaError(PipelineError):
    """Model output was not valid JSON or failed the expected schema."""


class PolicyError(PipelineError):
    """The model refused the request or a safety/policy check blocked it."""


class LowConfidenceError(PipelineError):
    """The model answered but confidence is below the deployment threshold."""


class NeedsHumanError(PipelineError):
    """Fail-closed exit: a human must review or take over.

    Wrap a more specific cause when one exists (timeout, schema, policy,
    low confidence, or a business rule that is HITL by design).
    """

    def __init__(self, reason: str, *, cause: Exception | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.cause = cause
