"""Assemble a pending dossier. This is not OCR — files are already .md/.txt."""

from __future__ import annotations

from pathlib import Path

from src.errors import ThinDossierError
from src.inbox import iter_files
from src.paths import MESSAGE_NAMES

MAX_CHARS = 20_000
MIN_CHARS = 200


def assemble_dossier(folder: Path) -> str:
    parts: list[str] = []
    files = iter_files(folder)
    message_files = [p for p in files if p.name in MESSAGE_NAMES]
    others = [p for p in files if p.name not in MESSAGE_NAMES]
    for path in message_files + others:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        parts.append(f"## {path.name}\n{text}")
    dossier = "\n\n".join(parts).strip()
    if len(dossier) < MIN_CHARS:
        raise ThinDossierError(
            f"Dossier is too thin ({len(dossier)} chars) to synthesize intake."
        )
    if len(dossier) > MAX_CHARS:
        raise ThinDossierError(
            f"Dossier exceeds {MAX_CHARS} characters; send to HITL instead of truncating."
        )
    return dossier
