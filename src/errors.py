"""Failure modes. Map these to HITL — never to a lead-facing side effect."""

from __future__ import annotations


class PipelineError(Exception):
    """Base error for the intake pipeline."""


class ConfigError(PipelineError):
    """Missing model/provider configuration."""


class LlmTimeoutError(PipelineError):
    """The model or downstream system did not respond in time."""


class LlmProviderError(PipelineError):
    """Auth, rate limit, or other provider failure."""


class SchemaError(PipelineError):
    """Model output was not valid JSON or failed the expected schema."""


class PolicyError(PipelineError):
    """The model refused the request or a safety/policy check blocked it."""


class LowConfidenceError(PipelineError):
    """The model answered but confidence is below the deployment threshold."""


class ThinDossierError(PipelineError):
    """Normalized pending files do not contain enough text to judge."""


class LeftoverBinaryError(PipelineError):
    """A non-text file is still in pending — extractor did not finish."""


class NeedsHumanError(PipelineError):
    """Fail-closed exit: a human must review or take over."""

    def __init__(self, reason: str, *, cause: Exception | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.cause = cause
