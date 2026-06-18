import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.zditm_szczecin.api import (
    API_BASE,
    ZditmApiError,
    ZditmConnectionError,
    fetch_display,
    fetch_lines,
    fetch_stops,
)


@pytest.mark.asyncio
async def test_fetch_display_returns_payload():
    payload = {
        "stop_name": "Brama Portowa",
        "stop_number": "11111",
        "departures": [{"line_number": "3", "direction": "Pomorzany", "time_real": 5, "time_scheduled": None}],
        "message": None,
        "updated_at": "2026-06-17T10:00:00+02:00",
    }
    with aioresponses() as mock:
        mock.get(f"{API_BASE}/displays/11111", payload=payload)
        async with aiohttp.ClientSession() as session:
            result = await fetch_display(session, "11111")
    assert result["stop_name"] == "Brama Portowa"
    assert result["departures"][0]["line_number"] == "3"


@pytest.mark.asyncio
async def test_fetch_stops_returns_data_list():
    with aioresponses() as mock:
        mock.get(f"{API_BASE}/stops", payload={"data": [{"id": 1, "number": "11111", "name": "Brama Portowa"}]})
        async with aiohttp.ClientSession() as session:
            result = await fetch_stops(session)
    assert result == [{"id": 1, "number": "11111", "name": "Brama Portowa"}]


@pytest.mark.asyncio
async def test_fetch_lines_returns_data_list():
    with aioresponses() as mock:
        mock.get(f"{API_BASE}/lines", payload={"data": [{"number": "3", "vehicle_type": "tram"}]})
        async with aiohttp.ClientSession() as session:
            result = await fetch_lines(session)
    assert result == [{"number": "3", "vehicle_type": "tram"}]


@pytest.mark.asyncio
async def test_non_200_raises_api_error():
    with aioresponses() as mock:
        mock.get(f"{API_BASE}/displays/99999", status=500)
        async with aiohttp.ClientSession() as session:
            with pytest.raises(ZditmApiError):
                await fetch_display(session, "99999")


@pytest.mark.asyncio
async def test_connection_failure_raises_connection_error():
    with aioresponses() as mock:
        mock.get(f"{API_BASE}/displays/11111", exception=aiohttp.ClientError("boom"))
        async with aiohttp.ClientSession() as session:
            with pytest.raises(ZditmConnectionError):
                await fetch_display(session, "11111")
