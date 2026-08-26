"""LiteLLM is the only model adapter. MAF does not choose the provider."""

from __future__ import annotations

import os
from typing import Any

from src.errors import ConfigError, LlmProviderError, LlmTimeoutError, PolicyError
from src.schema import schema_instruction


def _timeout_seconds() -> float:
    return float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))


def call_llm(dossier: str) -> str:
    """Call the configured model. Raises typed errors; never emails the lead."""
    model = os.getenv("LLM_MODEL")
    if not model:
        raise ConfigError(
            "LLM_MODEL is not set. Use --assemble-only or add LLM_MODEL to .env."
        )
    try:
        from litellm import completion
    except ImportError as exc:
        raise ConfigError("litellm is not installed. pip install -r requirements.txt") from exc

    prompt = (
        "You are structuring a software-consultancy project intake from a lead dossier.\n"
        f"{schema_instruction()}\n\nDossier:\n{dossier}"
    )
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=_timeout_seconds(),
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        name = type(exc).__name__.lower()
        message = str(exc).lower()
        if "timeout" in name or "timeout" in message:
            raise LlmTimeoutError("LLM timeout") from exc
        if "content" in message and ("filter" in message or "policy" in message or "safety" in message):
            raise PolicyError("Provider content policy blocked the request") from exc
        if "auth" in message or "api key" in message or "401" in message:
            raise LlmProviderError("LLM authentication failed") from exc
        raise LlmProviderError(f"LLM provider error: {exc}") from exc

    content = _message_content(response)
    if not content or not str(content).strip():
        raise PolicyError("Model returned empty content")
    return str(content)


def _message_content(response: Any) -> str:
    try:
        return response.choices[0].message.content or ""
    except (AttributeError, IndexError, KeyError):
        return ""
