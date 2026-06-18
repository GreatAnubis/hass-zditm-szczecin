"""ZDiTM Szczecin Home Assistant integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ZditmApiError, fetch_lines
from .const import CONF_REFRESH, CONF_STOP_NUMBER, DEFAULT_REFRESH, DOMAIN
from .coordinator import ZditmCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def _get_line_index(hass: HomeAssistant, session) -> dict:
    """Fetch and cache the /lines index (number -> info) shared across entries."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if "line_index" not in domain_data:
        try:
            lines = await fetch_lines(session)
            domain_data["line_index"] = {str(l.get("number")): l for l in lines}
        except ZditmApiError as err:
            _LOGGER.warning("Could not fetch /lines, using heuristic classification: %s", err)
            domain_data["line_index"] = {}
    return domain_data["line_index"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a stop from a config entry."""
    session = async_get_clientsession(hass)
    line_index = await _get_line_index(hass, session)

    refresh = entry.options.get(CONF_REFRESH, DEFAULT_REFRESH)
    coordinator = ZditmCoordinator(
        hass,
        session=session,
        stop_number=entry.data[CONF_STOP_NUMBER],
        refresh=refresh,
        line_index=line_index,
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {}).setdefault("entries", {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN]["entries"].pop(entry.entry_id, None)
    return unloaded


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
