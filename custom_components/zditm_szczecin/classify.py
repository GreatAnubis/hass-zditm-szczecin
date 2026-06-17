"""Line classification — port of the card's categorize() (src/format.ts)."""
from __future__ import annotations

import re

# Szczecin tram lines, verified against /api/v1/lines vehicle_type (2026-06-16).
DEFAULT_TRAM_LINES = [str(n) for n in range(1, 12)]  # "1".."11"

# Badge colors, identical to the published zditm-departures-card.
BADGE_COLORS = {
    "tram": {"background": "#2e7d32", "text": "#ffffff"},
    "bus": {"background": "#1565c0", "text": "#ffffff"},
    "fast": {"background": "#c62828", "text": "#ffffff"},
    "night": {"background": "#37474f", "text": "#ffffff"},
    "replacement": {"background": "#f9a825", "text": "#1b1b1b"},
}


def categorize(line_number: str | int, info: dict | None, tram_lines: list) -> str:
    """Return badge category from /lines info, falling back to a number heuristic."""
    if info:
        if info.get("vehicle_type") == "tram":
            return "tram"
        if info.get("type") == "night":
            return "night"
        if info.get("subtype") == "fast":
            return "fast"
        if info.get("subtype") == "replacement":
            return "replacement"
        return "bus"

    s = str(line_number)
    if s in {str(x) for x in tram_lines}:
        return "tram"
    if re.match(r"^[A-Za-z]", s):
        return "fast"
    if re.match(r"^5\d{2}$", s):
        return "night"
    if re.match(r"^8\d{2}$", s):
        return "replacement"
    return "bus"
