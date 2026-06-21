"""Tests for the ZDiTM Szczecin config and options flow."""
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.zditm_szczecin.const import (
    CONF_PAIRS,
    CONF_REFRESH,
    CONF_STOP_NAME,
    CONF_STOP_NUMBER,
    DOMAIN,
)

STOPS = [
    {"id": 1, "number": "11111", "name": "Brama Portowa"},
    {"id": 2, "number": "22222", "name": "Plac Rodla"},
]
DISPLAY = {
    "stop_name": "Brama Portowa",
    "stop_number": "11111",
    "message": None,
    "updated_at": "2026-06-17T10:00:00+02:00",
    "departures": [
        {"line_number": "3", "direction": "Pomorzany", "time_real": 5, "time_scheduled": None},
        {"line_number": "7", "direction": "Krzekowo", "time_real": 9, "time_scheduled": None},
    ],
}


@pytest.mark.asyncio
async def test_full_config_flow_creates_entry(hass):
    with patch("custom_components.zditm_szczecin.config_flow.fetch_stops", new=AsyncMock(return_value=STOPS)), \
         patch("custom_components.zditm_szczecin.config_flow.fetch_display", new=AsyncMock(return_value=DISPLAY)):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {"query": "Brama"})
        assert result["step_id"] == "select_stop"

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_STOP_NUMBER: "11111"})
        assert result["step_id"] == "pairs"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_PAIRS: [], CONF_REFRESH: "60"}
        )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_STOP_NUMBER] == "11111"
    assert result["options"][CONF_REFRESH] == 60


@pytest.mark.asyncio
async def test_duplicate_stop_aborts(hass):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STOP_NUMBER: "11111", CONF_STOP_NAME: "Brama Portowa"},
        unique_id="11111",
    ).add_to_hass(hass)

    with patch("custom_components.zditm_szczecin.config_flow.fetch_stops", new=AsyncMock(return_value=STOPS)), \
         patch("custom_components.zditm_szczecin.config_flow.fetch_display", new=AsyncMock(return_value=DISPLAY)):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {"query": "Brama"})
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_STOP_NUMBER: "11111"})

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_options_flow_updates_refresh(hass):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STOP_NUMBER: "11111", CONF_STOP_NAME: "Brama Portowa"},
        options={CONF_PAIRS: [], CONF_REFRESH: 60},
        unique_id="11111",
    )
    entry.add_to_hass(hass)
    with patch("custom_components.zditm_szczecin.fetch_lines", new=AsyncMock(return_value=[])), \
         patch("custom_components.zditm_szczecin.coordinator.fetch_display", new=AsyncMock(return_value=DISPLAY)), \
         patch("custom_components.zditm_szczecin.config_flow.fetch_display", new=AsyncMock(return_value=DISPLAY)):
        assert await hass.config_entries.async_setup(entry.entry_id) is True
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["step_id"] == "init"
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_PAIRS: [], CONF_REFRESH: "90"}
        )
        assert result["type"] == "create_entry"

    assert entry.options[CONF_REFRESH] == 90


def test_served_directions_unique_and_capped():
    from custom_components.zditm_szczecin.config_flow import _served_directions

    display = {
        "departures": [
            {"line_number": "3", "direction": "Pomorzany"},
            {"line_number": "7", "direction": "Pomorzany"},  # duplicate direction
            {"line_number": "1", "direction": "Głębokie"},
            {"line_number": "9", "direction": "Krzekowo"},
            {"line_number": "2", "direction": "Basen Górniczy"},  # beyond limit=3
        ]
    }
    assert _served_directions(display, limit=3) == ["Pomorzany", "Głębokie", "Krzekowo"]
    assert _served_directions({"departures": []}) == []


def test_stop_label_with_and_without_directions():
    from custom_components.zditm_szczecin.config_flow import _stop_label

    stop = {"name": "Brama Portowa", "number": "11111"}
    assert _stop_label(stop, ["Pomorzany", "Głębokie"]) == "Brama Portowa (11111) → Pomorzany, Głębokie"
    assert _stop_label(stop, []) == "Brama Portowa (11111)"
