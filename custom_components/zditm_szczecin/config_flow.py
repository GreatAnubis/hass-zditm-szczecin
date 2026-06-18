"""Config flow stub — full implementation in Task 7."""
from __future__ import annotations

from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN


class ZditmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Placeholder config flow; full implementation in Task 7."""

    VERSION = 1
