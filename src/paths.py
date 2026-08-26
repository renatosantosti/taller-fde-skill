"""Repository paths. Windows-safe pathlib."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INBOX_ROOT = REPO_ROOT / "inbox"
BUS_ROOT = REPO_ROOT / "bus"
CHECKPOINTS_ROOT = REPO_ROOT / "checkpoints"
LEAD_INDEX_DIR = CHECKPOINTS_ROOT / "leads"

STAGES = ("input", "pending", "in_analysis", "completed", "needs_human")
ALLOWED_TEXT_SUFFIXES = {".txt", ".md"}
MESSAGE_NAMES = ("default.message.txt", "default.message.md")
