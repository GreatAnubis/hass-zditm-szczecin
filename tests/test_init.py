from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.zditm_szczecin.const import (
    CONF_STOP_NAME,
    CONF_STOP_NUMBER,
    DOMAIN,
)

RAW_DISPLAY = {
    "stop_name": "Brama Portowa",
    "stop_number": "11111",
    "message": None,
    "updated_at": "2026-06-17T10:00:00+02:00",
    "departures": [{"line_number": "3", "direction": "Pomorzany", "time_real": 5, "time_scheduled": None}],
}


def _entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STOP_NUMBER: "11111", CONF_STOP_NAME: "Brama Portowa"},
        options={},
        unique_id="11111",
    )


@pytest.mark.asyncio
async def test_setup_and_unload_entry(hass):
    entry = _entry()
    entry.add_to_hass(hass)
    with patch(
        "custom_components.zditm_szczecin.fetch_lines",
        new=AsyncMock(return_value=[{"number": "3", "vehicle_type": "tram"}]),
    ), patch(
        "custom_components.zditm_szczecin.coordinator.fetch_display",
        new=AsyncMock(return_value=RAW_DISPLAY),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id) is True
        await hass.async_block_till_done()
        assert entry.entry_id in hass.data[DOMAIN]["entries"]

        assert await hass.config_entries.async_unload(entry.entry_id) is True
        await hass.async_block_till_done()
        assert entry.entry_id not in hass.data[DOMAIN]["entries"]
