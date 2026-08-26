"""Shared fixtures. Inbox/bus/checkpoints are isolated under tmp_path."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src.paths import REPO_ROOT, STAGES


@pytest.fixture
def inbox_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    inbox = tmp_path / "inbox"
    for stage in STAGES:
        (inbox / stage).mkdir(parents=True)
    src_pending = REPO_ROOT / "inbox" / "pending"
    for name in ("lead-happy", "lead-ambiguous", "lead-thin"):
        shutil.copytree(src_pending / name, inbox / "pending" / name)
    monkeypatch.setattr("src.inbox.INBOX_ROOT", inbox)
    return inbox


@pytest.fixture
def roots(
    inbox_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    bus_root = tmp_path / "bus"
    checkpoints = tmp_path / "checkpoints"
    monkeypatch.setattr("src.workflow.CHECKPOINTS_ROOT", checkpoints)
    monkeypatch.setattr("src.workflow.LEAD_INDEX_DIR", checkpoints / "leads")
    return inbox_root, bus_root, checkpoints
