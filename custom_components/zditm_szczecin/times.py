"""Minute computation — port of the card's departureRelative() (src/format.ts)."""
from __future__ import annotations

import re
from datetime import datetime, timedelta

_HHMM = re.compile(r"^(\d{1,2}):(\d{2})$")


def is_live(time_real: int | None) -> bool:
    """Whether this departure has a live (GPS) prediction."""
    return time_real is not None


def compute_minutes(time_real: int | None, time_scheduled: str | None, now: datetime) -> int | None:
    """Minutes until departure. Live value wins; else parse hh:mm with day-rollover."""
    if time_real is not None:
        return time_real
    if time_scheduled:
        m = _HHMM.match(time_scheduled.strip())
        if not m:
            return None
        target = now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
        if target < now - timedelta(seconds=60):
            target += timedelta(days=1)
        diff = round((target - now).total_seconds() / 60)
        return max(diff, 0)
    return None
