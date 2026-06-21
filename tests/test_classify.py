from custom_components.zditm_szczecin.classify import (
    categorize,
    DEFAULT_TRAM_LINES,
    BADGE_COLORS,
)


def test_tram_from_vehicle_type():
    assert categorize("3", {"vehicle_type": "tram"}, DEFAULT_TRAM_LINES) == "tram"


def test_night_from_type():
    assert categorize("521", {"vehicle_type": "bus", "type": "night"}, DEFAULT_TRAM_LINES) == "night"


def test_fast_from_subtype():
    assert categorize("A", {"vehicle_type": "bus", "subtype": "fast"}, DEFAULT_TRAM_LINES) == "fast"


def test_replacement_from_subtype():
    assert categorize("821", {"vehicle_type": "bus", "subtype": "replacement"}, DEFAULT_TRAM_LINES) == "replacement"


def test_plain_bus_with_info():
    assert categorize("75", {"vehicle_type": "bus"}, DEFAULT_TRAM_LINES) == "bus"


def test_fallback_tram_by_default_list():
    assert categorize("3", None, DEFAULT_TRAM_LINES) == "tram"


def test_fallback_fast_by_letter():
    assert categorize("B", None, DEFAULT_TRAM_LINES) == "fast"


def test_fallback_night_by_5xx():
    assert categorize("521", None, DEFAULT_TRAM_LINES) == "night"


def test_fallback_replacement_by_8xx():
    assert categorize("821", None, DEFAULT_TRAM_LINES) == "replacement"


def test_fallback_bus_default():
    assert categorize("75", None, DEFAULT_TRAM_LINES) == "bus"


def test_badge_colors_match_card():
    assert BADGE_COLORS["tram"]["background"] == "#2e7d32"
    assert BADGE_COLORS["bus"]["background"] == "#1565c0"
    assert BADGE_COLORS["fast"]["background"] == "#c62828"
    assert BADGE_COLORS["night"]["background"] == "#37474f"
    assert BADGE_COLORS["replacement"]["background"] == "#f9a825"
    assert BADGE_COLORS["replacement"]["text"] == "#1b1b1b"
    # all non-replacement categories use white text
    assert BADGE_COLORS["tram"]["text"] == "#ffffff"
    assert BADGE_COLORS["bus"]["text"] == "#ffffff"
    assert BADGE_COLORS["fast"]["text"] == "#ffffff"
    assert BADGE_COLORS["night"]["text"] == "#ffffff"
