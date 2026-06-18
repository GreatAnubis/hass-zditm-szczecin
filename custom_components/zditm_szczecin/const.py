"""Constants and small helpers for the ZDiTM Szczecin integration."""
from __future__ import annotations

DOMAIN = "zditm_szczecin"

CONF_STOP_NUMBER = "stop_number"
CONF_STOP_NAME = "stop_name"
CONF_PAIRS = "pairs"
CONF_REFRESH = "refresh"

DEFAULT_REFRESH = 60
MIN_REFRESH = 30
REFRESH_OPTIONS = [30, 60, 90, 120, 300]

# Unit Separator — never appears in line numbers or direction names.
PAIR_SEP = "\x1f"


def encode_pair(line: str, direction: str) -> str:
    """Encode a (line, direction) pair into a single options-storable string."""
    return f"{line}{PAIR_SEP}{direction}"


def decode_pair(value: str) -> tuple[str, str]:
    """Decode a stored pair string back into (line, direction)."""
    line, _, direction = value.partition(PAIR_SEP)
    return line, direction
