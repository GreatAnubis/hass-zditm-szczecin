"""Tests for ZditmCoordinator."""
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.zditm_szczecin.const import (
    DEFAULT_REFRESH,
    decode_pair,
    encode_pair,
)
from custom_components.zditm_szczecin.coordinator import ZditmCoordinator


def test_encode_decode_pair_roundtrip():
    enc = encode_pair("3", "Pomorzany Dworzec")
    assert decode_pair(enc) == ("3", "Pomorzany Dworzec")


@pytest.mark.asyncio
async def test_coordinator_enriches_departures_with_category(hass):
    raw = {
        "stop_name": "Brama Portowa",
        "stop_number": "11111",
        "message": None,
        "updated_at": "2026-06-17T10:00:00+02:00",
        "departures": [
            {"line_number": "3", "direction": "Pomorzany", "time_real": 5, "time_scheduled": None},
            {"line_number": "521", "direction": "Police", "time_real": None, "time_scheduled": "23:58"},
        ],
    }
    line_index = {"3": {"vehicle_type": "tram"}, "521": {"vehicle_type": "bus", "type": "night"}}
    with patch(
        "custom_components.zditm_szczecin.coordinator.fetch_display",
        new=AsyncMock(return_value=raw),
    ):
        coord = ZditmCoordinator(hass, session=object(), stop_number="11111", refresh=DEFAULT_REFRESH, line_index=line_index)
        await coord.async_refresh()

    data = coord.data
    assert data["stop_name"] == "Brama Portowa"
    assert data["stop_number"] == "11111"
    assert data["message"] is None
    assert data["updated_at"] == "2026-06-17T10:00:00+02:00"
    assert data["departures"][0]["line"] == "3"
    assert data["departures"][0]["direction"] == "Pomorzany"
    assert data["departures"][0]["time_real"] == 5
    assert data["departures"][0]["time_scheduled"] is None
    assert data["departures"][0]["category"] == "tram"
    assert data["departures"][1]["line"] == "521"
    assert data["departures"][1]["time_scheduled"] == "23:58"
    assert data["departures"][1]["category"] == "night"


@pytest.mark.asyncio
async def test_coordinator_raises_update_failed_on_api_error(hass):
    from homeassistant.helpers.update_coordinator import UpdateFailed

    from custom_components.zditm_szczecin.api import ZditmApiError

    with patch(
        "custom_components.zditm_szczecin.coordinator.fetch_display",
        new=AsyncMock(side_effect=ZditmApiError("boom")),
    ):
        coord = ZditmCoordinator(hass, session=object(), stop_number="11111", refresh=DEFAULT_REFRESH, line_index={})
        with pytest.raises(UpdateFailed):
            await coord._async_update_data()
