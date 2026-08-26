"""Workflow helpers without a live MAF run."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.bus import FileBus
from src.errors import NeedsHumanError


class _NoPending:
    def __iter__(self):
        return iter([])

    def get_request_info_events(self):
        return []

    def get_outputs(self):
        return []


class _PendingNoCheckpoint:
    def __iter__(self):
        return iter([])

    def get_request_info_events(self):
        return [SimpleNamespace(request_id="req-1", data=None)]


class _RequestInfoEvent:
    type = "request_info"
    request_id = "req-fallback"
    data = "payload"


class _FallbackEvents:
    def __iter__(self):
        return iter([_RequestInfoEvent()])


@pytest.mark.asyncio
async def test_run_lead_ok_when_no_outputs(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Storage:
        async def get_latest(self, workflow_name=None):
            return None

    class Workflow:
        async def run(self, lead_id):
            return _NoPending()

    monkeypatch.setattr(
        "src.workflow.build_workflow", lambda **k: (Workflow(), Storage())
    )
    from src.workflow import run_lead

    result = await run_lead("lead-x", bus=FileBus(tmp_path / "bus"))
    assert result == {"status": "ok", "lead_id": "lead-x"}


@pytest.mark.asyncio
async def test_hitl_without_checkpoint_raises(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Storage:
        async def get_latest(self, workflow_name=None):
            return None

    class Workflow:
        async def run(self, lead_id):
            return _PendingNoCheckpoint()

    monkeypatch.setattr(
        "src.workflow.build_workflow", lambda **k: (Workflow(), Storage())
    )
    from src.workflow import run_lead

    with pytest.raises(NeedsHumanError, match="no checkpoint"):
        await run_lead("lead-x", bus=FileBus(tmp_path / "bus"))


@pytest.mark.asyncio
async def test_resume_without_outputs(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Storage:
        pass

    class Workflow:
        async def run(self, checkpoint_id=None, responses=None):
            return _NoPending()

    monkeypatch.setattr(
        "src.workflow.build_workflow", lambda **k: (Workflow(), Storage())
    )
    monkeypatch.setattr(
        "src.workflow.load_lead_index",
        lambda _id: {"checkpoint_id": "cp", "request_id": "req"},
    )
    from src.workflow import resume_lead

    result = await resume_lead(
        "lead-x", "bid", "ok", bus=FileBus(tmp_path / "bus")
    )
    assert result["status"] == "completed_after_hitl"
    assert result["decision"] == "bid"


def test_pending_requests_event_fallback() -> None:
    from src.workflow import _pending_requests

    pending = _pending_requests(_FallbackEvents())
    assert pending == [("req-fallback", "payload")]


def test_pending_requests_none() -> None:
    from src.workflow import _pending_requests

    assert _pending_requests(None) == []
