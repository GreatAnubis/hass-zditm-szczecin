"""Tests for ZDiTM Szczecin sensor entities (Task 6)."""
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.zditm_szczecin.const import (
    CONF_PAIRS,
    CONF_STOP_NAME,
    CONF_STOP_NUMBER,
    DOMAIN,
    encode_pair,
)

RAW_DISPLAY = {
    "stop_name": "Brama Portowa",
    "stop_number": "11111",
    "message": "Uwaga: objazd",
    "updated_at": "2026-06-17T10:00:00+02:00",
    "departures": [
        {"line_number": "3", "direction": "Pomorzany", "time_real": 5, "time_scheduled": None},
        {"line_number": "3", "direction": "Las Arkonski", "time_real": 12, "time_scheduled": None},
    ],
}


EMPTY_DISPLAY = {
    "stop_name": "Brama Portowa",
    "stop_number": "11111",
    "message": None,
    "updated_at": "2026-06-17T03:00:00+02:00",
    "departures": [],
}


async def _setup(hass, options, display=RAW_DISPLAY):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STOP_NUMBER: "11111", CONF_STOP_NAME: "Brama Portowa"},
        options=options,
        unique_id="11111",
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.zditm_szczecin.fetch_lines",
        new=AsyncMock(return_value=[{"number": "3", "vehicle_type": "tram"}]),
    ), patch(
        "custom_components.zditm_szczecin.coordinator.fetch_display",
        new=AsyncMock(return_value=display),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id) is True
        await hass.async_block_till_done()
    return entry


@pytest.mark.asyncio
async def test_stop_sensor_state_and_attributes(hass):
    await _setup(hass, options={})
    state = hass.states.get("sensor.brama_portowa_nastepny_odjazd")
    assert state is not None
    assert state.state == "5"
    assert state.attributes["message"] == "Uwaga: objazd"
    assert state.attributes["stop_number"] == "11111"
    assert len(state.attributes["departures"]) == 2
    assert state.attributes["departures"][0]["category"] == "tram"
    assert state.attributes["departures"][0]["minutes"] == 5


@pytest.mark.asyncio
async def test_line_direction_sensor_state(hass):
    pair = encode_pair("3", "Las Arkonski")
    await _setup(hass, options={CONF_PAIRS: [pair]})
    # entity for the selected pair reports minutes for that specific direction
    states = [s for s in hass.states.async_all("sensor") if s.attributes.get("direction") == "Las Arkonski"]
    assert len(states) == 1
    assert states[0].state == "12"
    assert states[0].attributes["line"] == "3"
    assert states[0].attributes["category"] == "tram"


@pytest.mark.asyncio
async def test_stop_sensor_empty_board(hass):
    # Night/horizon: empty departures -> state unknown, no crash, empty list in attributes
    await _setup(hass, options={}, display=EMPTY_DISPLAY)
    state = hass.states.get("sensor.brama_portowa_nastepny_odjazd")
    assert state is not None
    assert state.state == "unknown"
    assert state.attributes["departures"] == []
    assert state.attributes["message"] is None
