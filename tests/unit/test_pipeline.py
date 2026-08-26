"""CLI tests. Workflow and dotenv are mocked."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.errors import ConfigError, NeedsHumanError
from src.pipeline import main


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.pipeline.load_dotenv", lambda *a, **k: None)


def test_list(inbox_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "lead-happy" in out
    assert "lead-thin" in out


def test_assemble_only_success(inbox_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--assemble-only", "lead-happy"]) == 0
    assert "React" in capsys.readouterr().out


def test_assemble_only_thin(inbox_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--assemble-only", "lead-thin"]) == 1
    assert "needs_human" in capsys.readouterr().err


def test_assemble_only_requires_lead(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--assemble-only"]) == 2
    assert "assemble-only requires" in capsys.readouterr().err


def test_missing_lead_id(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "lead_id" in capsys.readouterr().err


def test_run_ok(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    async def fake_run(lead_id: str):
        return {"status": "ok", "lead_id": lead_id}

    monkeypatch.setattr("src.workflow.run_lead", fake_run)
    assert main(["lead-happy"]) == 0
    assert '"status": "ok"' in capsys.readouterr().out


def test_run_config_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    async def fake_run(_lead_id: str):
        raise ConfigError("LLM_MODEL is not set")

    monkeypatch.setattr("src.workflow.run_lead", fake_run)
    assert main(["lead-happy"]) == 2
    assert "config:" in capsys.readouterr().err


def test_run_needs_human(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    async def fake_run(_lead_id: str):
        raise NeedsHumanError("pause")

    monkeypatch.setattr("src.workflow.run_lead", fake_run)
    assert main(["lead-happy"]) == 1
    assert "needs_human: pause" in capsys.readouterr().err


def test_resume(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    async def fake_resume(lead_id: str, decision: str, notes: str):
        return {"status": "completed_after_hitl", "lead_id": lead_id, "decision": decision}

    monkeypatch.setattr("src.workflow.resume_lead", fake_resume)
    assert main(["resume", "lead-happy", "--decision", "bid", "--notes", "ok"]) == 0
    assert "completed_after_hitl" in capsys.readouterr().out
