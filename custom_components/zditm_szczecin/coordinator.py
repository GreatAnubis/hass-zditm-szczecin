"""Per-stop DataUpdateCoordinator for the ZDiTM Szczecin live board."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ZditmApiError, fetch_display
from .classify import DEFAULT_TRAM_LINES, categorize
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ZditmCoordinator(DataUpdateCoordinator):
    """Polls one stop's live board and enriches departures with a category."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        stop_number: str,
        refresh: int,
        line_index: dict,
        config_entry=None,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{stop_number}",
            update_interval=timedelta(seconds=refresh),
            config_entry=config_entry,
        )
        self._session = session
        self._stop_number = stop_number
        self._line_index = line_index or {}

    async def _async_update_data(self) -> dict:
        try:
            raw = await fetch_display(self._session, self._stop_number)
        except ZditmApiError as err:
            raise UpdateFailed(str(err)) from err

        departures = []
        for d in raw.get("departures", []):
            line = d.get("line_number")
            departures.append(
                {
                    "line": line,
                    "direction": d.get("direction"),
                    "time_real": d.get("time_real"),
                    "time_scheduled": d.get("time_scheduled"),
                    "category": categorize(line, self._line_index.get(str(line)), DEFAULT_TRAM_LINES),
                }
            )

        return {
            "stop_name": raw.get("stop_name"),
            "stop_number": raw.get("stop_number", self._stop_number),
            "message": raw.get("message"),
            "updated_at": raw.get("updated_at"),
            "departures": departures,
        }
