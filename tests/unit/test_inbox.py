"""Unit tests for deterministic inbox rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.errors import LeftoverBinaryError, NeedsHumanError
from src.inbox import (
    MAX_FILES,
    claim,
    find_lead,
    list_pending,
    move_lead,
    validate_pending,
)


def test_list_pending_empty_when_dir_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.inbox.INBOX_ROOT", tmp_path / "no-inbox")
    assert list_pending() == []


def test_validate_empty_folder(inbox_root: Path) -> None:
    empty = inbox_root / "pending" / "empty-lead"
    empty.mkdir()
    with pytest.raises(NeedsHumanError, match="empty"):
        validate_pending(empty)


def test_validate_missing_message_file(inbox_root: Path) -> None:
    folder = inbox_root / "pending" / "no-message"
    folder.mkdir()
    (folder / "notes.md").write_text("x" * 50, encoding="utf-8")
    with pytest.raises(NeedsHumanError, match="Missing required message"):
        validate_pending(folder)


def test_validate_leftover_binary(inbox_root: Path) -> None:
    folder = inbox_root / "pending" / "lead-happy"
    (folder / "scan.pdf").write_bytes(b"%PDF-fake")
    with pytest.raises(LeftoverBinaryError, match="scan.pdf"):
        validate_pending(folder)


def test_validate_too_many_files(inbox_root: Path) -> None:
    folder = inbox_root / "pending" / "lead-happy"
    for i in range(MAX_FILES):
        (folder / f"extra-{i}.txt").write_text("n", encoding="utf-8")
    with pytest.raises(NeedsHumanError, match="More than"):
        validate_pending(folder)


def test_find_lead_missing(inbox_root: Path) -> None:
    with pytest.raises(NeedsHumanError, match="not found"):
        find_lead("does-not-exist")


def test_claim_idempotent_and_missing(inbox_root: Path) -> None:
    first = claim("lead-happy")
    second = claim("lead-happy")
    assert first == second
    assert "lead-happy" not in list_pending()
    with pytest.raises(NeedsHumanError, match="not in pending"):
        claim("ghost")


def test_move_lead_overwrite(inbox_root: Path) -> None:
    dest = inbox_root / "completed" / "lead-happy"
    dest.mkdir()
    (dest / "old.txt").write_text("stale", encoding="utf-8")
    moved = move_lead("lead-happy", "completed")
    assert moved == dest
    assert not (dest / "old.txt").exists()
    assert (dest / "default.message.txt").exists()
    same = move_lead("lead-happy", "completed")
    assert same == dest
