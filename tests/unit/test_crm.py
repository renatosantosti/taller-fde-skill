"""CRM stub must not raise or call a live system."""

from src.crm import record_intake


def test_record_intake_is_noop() -> None:
    assert record_intake("lead-x", {"summary": "x"}, "bid") is None
    assert record_intake("lead-x", None, None) is None
