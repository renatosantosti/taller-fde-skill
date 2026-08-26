"""LiteLLM is mocked. No provider keys, no network."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.errors import ConfigError, LlmProviderError, LlmTimeoutError, PolicyError
from src.llm import call_llm


def _response(content: str | None) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_missing_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_MODEL", raising=False)
    with pytest.raises(ConfigError, match="LLM_MODEL"):
        call_llm("dossier")


def test_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")

    def fake_completion(**kwargs):
        assert kwargs["model"] == "fake-model"
        assert kwargs["response_format"] == {"type": "json_object"}
        return _response('{"summary":"ok"}')

    monkeypatch.setattr("litellm.completion", fake_completion)
    assert call_llm("dossier") == '{"summary":"ok"}'


def test_empty_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")
    monkeypatch.setattr("litellm.completion", lambda **k: _response("  "))
    with pytest.raises(PolicyError, match="empty"):
        call_llm("dossier")


def test_malformed_response_is_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")
    monkeypatch.setattr("litellm.completion", lambda **k: SimpleNamespace(choices=[]))
    with pytest.raises(PolicyError, match="empty"):
        call_llm("dossier")


def test_timeout_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")

    def boom(**kwargs):
        raise TimeoutError("request timeout")

    monkeypatch.setattr("litellm.completion", boom)
    with pytest.raises(LlmTimeoutError):
        call_llm("dossier")


def test_policy_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")

    def boom(**kwargs):
        raise RuntimeError("content filter / safety policy")

    monkeypatch.setattr("litellm.completion", boom)
    with pytest.raises(PolicyError, match="policy"):
        call_llm("dossier")


def test_auth_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")

    def boom(**kwargs):
        raise RuntimeError("401 invalid api key")

    monkeypatch.setattr("litellm.completion", boom)
    with pytest.raises(LlmProviderError, match="authentication"):
        call_llm("dossier")


def test_generic_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")

    def boom(**kwargs):
        raise RuntimeError("upstream 503")

    monkeypatch.setattr("litellm.completion", boom)
    with pytest.raises(LlmProviderError, match="503"):
        call_llm("dossier")


def test_litellm_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "fake-model")
    monkeypatch.setitem(__import__("sys").modules, "litellm", None)
    with pytest.raises(ConfigError, match="litellm is not installed"):
        call_llm("dossier")
