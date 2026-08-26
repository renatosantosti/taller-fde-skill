"""MAF workflow in-process. LiteLLM is mocked — no live provider."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.bus import TOPIC_DECISION, TOPIC_REVIEW, FileBus
from src.errors import LlmTimeoutError, NeedsHumanError, PolicyError, SchemaError
from src.inbox import list_pending

VALID_INTAKE = json.dumps(
    {
        "summary": "Rebuild a customer portal",
        "problem": "Legacy jQuery UI and SOAP billing",
        "constraints": ["Discovery first"],
        "suggested_engagement": "product",
        "urgency": "medium",
        "confidence": 0.9,
        "open_questions": ["ERP vendor"],
    }
)

UNKNOWN_INTAKE = json.dumps(
    {
        "summary": "Unclear request",
        "problem": "Unknown",
        "constraints": [],
        "suggested_engagement": "unknown",
        "urgency": "low",
        "confidence": 0.2,
        "open_questions": ["What do they want?"],
    }
)


@pytest.mark.asyncio
async def test_happy_path_completes_without_hitl(
    roots: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox, bus_root, _ = roots
    bus = FileBus(bus_root)
    monkeypatch.setattr("src.workflow.call_llm", lambda _d: VALID_INTAKE)
    from src.workflow import run_lead

    result = await run_lead("lead-happy", bus=bus)
    assert result["status"] == "ok"
    assert (inbox / "completed" / "lead-happy" / "intake.json").exists()


@pytest.mark.asyncio
async def test_hitl_pause_and_resume_decline_without_second_llm_call(
    roots: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox, bus_root, _ = roots
    bus = FileBus(bus_root)
    calls = {"n": 0}

    def fake_llm(_dossier: str) -> str:
        calls["n"] += 1
        return UNKNOWN_INTAKE

    monkeypatch.setattr("src.workflow.call_llm", fake_llm)
    from src.workflow import resume_lead, run_lead

    paused = await run_lead("lead-ambiguous", bus=bus)
    assert paused["status"] == "needs_human"
    assert calls["n"] == 1
    assert bus.get(TOPIC_REVIEW, "lead-ambiguous") is not None
    assert (inbox / "needs_human" / "lead-ambiguous" / "hitl.md").exists()

    resumed = await resume_lead("lead-ambiguous", "decline", "Out of fit", bus=bus)
    assert resumed["status"] == "completed_after_hitl"
    assert resumed["decision"] == "decline"
    assert calls["n"] == 1
    assert bus.get(TOPIC_DECISION, "lead-ambiguous")["decision"] == "decline"
    assert (inbox / "completed" / "lead-ambiguous" / "intake.json").exists()


@pytest.mark.asyncio
async def test_thin_dossier_hitl_skips_llm(
    roots: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox, bus_root, _ = roots
    bus = FileBus(bus_root)
    calls = {"n": 0}

    def fake_llm(_dossier: str) -> str:
        calls["n"] += 1
        return VALID_INTAKE

    monkeypatch.setattr("src.workflow.call_llm", fake_llm)
    from src.workflow import run_lead

    paused = await run_lead("lead-thin", bus=bus)
    assert paused["status"] == "needs_human"
    assert calls["n"] == 0
    assert "thin" in bus.get(TOPIC_REVIEW, "lead-thin")["reason"].lower()
    assert (inbox / "needs_human" / "lead-thin" / "hitl.md").exists()


@pytest.mark.asyncio
async def test_leftover_binary_hitl_skips_llm(
    roots: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox, bus_root, _ = roots
    (inbox / "pending" / "lead-happy" / "scan.pdf").write_bytes(b"%PDF-fake")
    bus = FileBus(bus_root)
    calls = {"n": 0}

    def fake_llm(_dossier: str) -> str:
        calls["n"] += 1
        return VALID_INTAKE

    monkeypatch.setattr("src.workflow.call_llm", fake_llm)
    from src.workflow import run_lead

    paused = await run_lead("lead-happy", bus=bus)
    assert paused["status"] == "needs_human"
    assert calls["n"] == 0
    assert "pdf" in bus.get(TOPIC_REVIEW, "lead-happy")["reason"].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc",
    [
        SchemaError("bad json"),
        PolicyError("refused"),
        LlmTimeoutError("LLM timeout"),
    ],
)
async def test_llm_failures_go_to_hitl(
    roots: tuple[Path, Path, Path],
    monkeypatch: pytest.MonkeyPatch,
    exc: Exception,
) -> None:
    _inbox, bus_root, _ = roots
    bus = FileBus(bus_root)

    def boom(_dossier: str) -> str:
        raise exc

    monkeypatch.setattr("src.workflow.call_llm", boom)
    from src.workflow import run_lead

    paused = await run_lead("lead-happy", bus=bus)
    assert paused["status"] == "needs_human"
    assert str(exc) in bus.get(TOPIC_REVIEW, "lead-happy")["reason"]


@pytest.mark.asyncio
async def test_resume_bid_and_invalid_decision_coerced(
    roots: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    inbox, bus_root, _ = roots
    bus = FileBus(bus_root)
    monkeypatch.setattr("src.workflow.call_llm", lambda _d: UNKNOWN_INTAKE)
    from src.workflow import resume_lead, run_lead

    await run_lead("lead-ambiguous", bus=bus)
    bid = await resume_lead("lead-ambiguous", "bid", "fits", bus=bus)
    assert bid["decision"] == "bid"
    assert (inbox / "completed" / "lead-ambiguous" / "intake.json").exists()


@pytest.mark.asyncio
async def test_resume_invalid_decision_becomes_request_call(
    roots: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _inbox, bus_root, _ = roots
    bus = FileBus(bus_root)
    monkeypatch.setattr("src.workflow.call_llm", lambda _d: UNKNOWN_INTAKE)
    from src.workflow import resume_lead, run_lead

    await run_lead("lead-happy", bus=bus)
    result = await resume_lead("lead-happy", "maybe-later", "", bus=bus)
    assert result["decision"] == "request_call"


def test_load_lead_index_missing(roots: tuple[Path, Path, Path]) -> None:
    from src.workflow import load_lead_index

    with pytest.raises(NeedsHumanError, match="No HITL checkpoint"):
        load_lead_index("never-ran")


def test_list_pending_from_isolated_inbox(inbox_root: Path) -> None:
    assert set(list_pending()) == {"lead-ambiguous", "lead-happy", "lead-thin"}
