"""Unit tests for dossier assembly (not OCR)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.assemble import assemble_dossier
from src.errors import ThinDossierError


def test_assemble_happy_includes_table_and_caption(inbox_root: Path) -> None:
    text = assemble_dossier(inbox_root / "pending" / "lead-happy")
    assert "React" in text
    assert "Image description" in text
    assert "## default.message.txt" in text


def test_assemble_thin_fails(inbox_root: Path) -> None:
    with pytest.raises(ThinDossierError, match="too thin"):
        assemble_dossier(inbox_root / "pending" / "lead-thin")


def test_assemble_over_cap(inbox_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.assemble.MAX_CHARS", 50)
    with pytest.raises(ThinDossierError, match="exceeds"):
        assemble_dossier(inbox_root / "pending" / "lead-happy")
