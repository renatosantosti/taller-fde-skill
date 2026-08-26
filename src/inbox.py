"""Deterministic inbox: list, validate, claim, move. Never walks inbox/input/."""

from __future__ import annotations

import shutil
from pathlib import Path

from src.errors import LeftoverBinaryError, NeedsHumanError
from src.paths import ALLOWED_TEXT_SUFFIXES, INBOX_ROOT, MESSAGE_NAMES

MAX_FILES = 8


def stage_dir(stage: str) -> Path:
    return INBOX_ROOT / stage


def lead_dir(stage: str, lead_id: str) -> Path:
    return stage_dir(stage) / lead_id


def list_pending() -> list[str]:
    pending = stage_dir("pending")
    if not pending.exists():
        return []
    return sorted(p.name for p in pending.iterdir() if p.is_dir())


def find_lead(lead_id: str) -> Path:
    """Locate a lead folder in pending or in_analysis (claimed)."""
    for stage in ("pending", "in_analysis", "needs_human", "completed"):
        path = lead_dir(stage, lead_id)
        if path.is_dir():
            return path
    raise NeedsHumanError(f"Lead folder not found: {lead_id}")


def iter_files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.is_file() and p.name != ".gitkeep")


def validate_pending(folder: Path) -> None:
    files = iter_files(folder)
    if not files:
        raise NeedsHumanError("Pending folder is empty.")
    names = {p.name for p in files}
    if not any(name in names for name in MESSAGE_NAMES):
        raise NeedsHumanError(
            f"Missing required message file ({' or '.join(MESSAGE_NAMES)})."
        )
    leftover = [p.name for p in files if p.suffix.lower() not in ALLOWED_TEXT_SUFFIXES]
    if leftover:
        raise LeftoverBinaryError(
            f"Non-text files in pending (extractor did not finish): {leftover}"
        )
    if len(files) > MAX_FILES:
        raise NeedsHumanError(f"More than {MAX_FILES} files; refuse to assemble silently.")


def claim(lead_id: str) -> Path:
    """Move pending → in_analysis. Idempotent if already claimed."""
    pending = lead_dir("pending", lead_id)
    analysis = lead_dir("in_analysis", lead_id)
    if analysis.is_dir():
        return analysis
    if not pending.is_dir():
        raise NeedsHumanError(f"Cannot claim {lead_id}: not in pending.")
    analysis.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(pending), str(analysis))
    return analysis


def move_lead(lead_id: str, dest_stage: str) -> Path:
    current = find_lead(lead_id)
    dest = lead_dir(dest_stage, lead_id)
    if current.resolve() == dest.resolve():
        return dest
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(current), str(dest))
    return dest
