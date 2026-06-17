from datetime import datetime

from custom_components.zditm_szczecin.times import compute_minutes, is_live


def test_live_minutes_passthrough():
    assert compute_minutes(16, None, datetime(2026, 6, 16, 22, 15)) == 16


def test_live_zero_is_zero():
    assert compute_minutes(0, None, datetime(2026, 6, 16, 22, 15)) == 0


def test_scheduled_minutes_until():
    assert compute_minutes(None, "22:35", datetime(2026, 6, 16, 22, 15)) == 20


def test_scheduled_rolls_past_midnight():
    assert compute_minutes(None, "00:58", datetime(2026, 6, 16, 23, 58)) == 60


def test_scheduled_already_passed_rolls_to_next_day():
    # 22:00 is 15 min before 22:15 -> treated as tomorrow (card behavior)
    assert compute_minutes(None, "22:00", datetime(2026, 6, 16, 22, 15)) == 60 * 24 - 15


def test_invalid_scheduled_returns_none():
    assert compute_minutes(None, "garbage", datetime(2026, 6, 16, 22, 15)) is None


def test_both_none_returns_none():
    assert compute_minutes(None, None, datetime(2026, 6, 16, 22, 15)) is None


def test_is_live():
    assert is_live(3) is True
    assert is_live(0) is True
    assert is_live(None) is False
