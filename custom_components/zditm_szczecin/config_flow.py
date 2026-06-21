"""Config and options flow for ZDiTM Szczecin."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import ZditmApiError, fetch_display, fetch_stops
from .const import (
    CONF_PAIRS,
    CONF_REFRESH,
    CONF_STOP_NAME,
    CONF_STOP_NUMBER,
    DEFAULT_REFRESH,
    DOMAIN,
    REFRESH_OPTIONS,
    encode_pair,
)


def _pair_options(display: dict) -> list[SelectOptionDict]:
    """Build unique (line, direction) select options from a live board."""
    seen: dict[str, str] = {}
    for d in display.get("departures", []):
        value = encode_pair(d.get("line_number"), d.get("direction"))
        seen[value] = f"{d.get('line_number')} → {d.get('direction')}"
    return [SelectOptionDict(value=v, label=lbl) for v, lbl in seen.items()]


def _refresh_selector() -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=[SelectOptionDict(value=str(s), label=f"{s} s") for s in REFRESH_OPTIONS],
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


class ZditmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the ZDiTM Szczecin config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._matches: list[dict] = []
        self._stop_number: str | None = None
        self._stop_name: str | None = None
        self._pair_opts: list[SelectOptionDict] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial search step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                stops = await fetch_stops(session)
            except ZditmApiError:
                errors["base"] = "cannot_connect"
            else:
                query = user_input["query"].strip().lower()
                self._matches = [s for s in stops if query in s.get("name", "").lower()]
                if not self._matches:
                    errors["query"] = "no_stops"
                else:
                    return await self.async_step_select_stop()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("query"): str}),
            errors=errors,
        )

    async def async_step_select_stop(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the stop selection step."""
        if user_input is not None:
            self._stop_number = user_input[CONF_STOP_NUMBER]
            match = next((s for s in self._matches if s["number"] == self._stop_number), None)
            self._stop_name = match["name"] if match else self._stop_number

            await self.async_set_unique_id(self._stop_number)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            try:
                display = await fetch_display(session, self._stop_number)
            except ZditmApiError:
                display = {"departures": []}
            self._pair_opts = _pair_options(display)
            return await self.async_step_pairs()

        options = [
            SelectOptionDict(value=s["number"], label=f"{s['name']} ({s['number']})")
            for s in self._matches
        ]
        return self.async_show_form(
            step_id="select_stop",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_STOP_NUMBER): SelectSelector(
                        SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
        )

    async def async_step_pairs(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the line+direction pairs and refresh interval step."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"{self._stop_name} ({self._stop_number})",
                data={CONF_STOP_NUMBER: self._stop_number, CONF_STOP_NAME: self._stop_name},
                options={
                    CONF_PAIRS: user_input.get(CONF_PAIRS, []),
                    CONF_REFRESH: int(user_input.get(CONF_REFRESH, DEFAULT_REFRESH)),
                },
            )
        return self.async_show_form(
            step_id="pairs",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PAIRS, default=[]): SelectSelector(
                        SelectSelectorConfig(
                            options=self._pair_opts, multiple=True, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Optional(CONF_REFRESH, default=str(DEFAULT_REFRESH)): _refresh_selector(),
                }
            ),
            description_placeholders={"count": str(len(self._pair_opts))},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow.

        HA calls this with the entry, but modern OptionsFlow takes no constructor
        arg and reads `self.config_entry` (a framework-provided property).
        """
        return ZditmOptionsFlow()


class ZditmOptionsFlow(OptionsFlow):
    """Edit tracked pairs and refresh interval."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle options flow initialisation."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_PAIRS: user_input.get(CONF_PAIRS, []),
                    CONF_REFRESH: int(user_input.get(CONF_REFRESH, DEFAULT_REFRESH)),
                },
            )

        session = async_get_clientsession(self.hass)
        try:
            display = await fetch_display(session, self.config_entry.data[CONF_STOP_NUMBER])
        except ZditmApiError:
            display = {"departures": []}
        pair_opts = _pair_options(display)
        current_pairs = self.config_entry.options.get(CONF_PAIRS, [])
        # Keep any currently-selected pair even if not on the board right now.
        known = {o["value"] for o in pair_opts}
        for value in current_pairs:
            if value not in known:
                line, _, direction = value.partition("\x1f")
                pair_opts.append(SelectOptionDict(value=value, label=f"{line} → {direction}"))

        current_refresh = str(self.config_entry.options.get(CONF_REFRESH, DEFAULT_REFRESH))
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PAIRS, default=current_pairs): SelectSelector(
                        SelectSelectorConfig(
                            options=pair_opts, multiple=True, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Optional(CONF_REFRESH, default=current_refresh): _refresh_selector(),
                }
            ),
        )
