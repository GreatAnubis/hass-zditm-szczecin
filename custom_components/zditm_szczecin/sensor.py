"""Sensor entities for ZDiTM Szczecin departures."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PAIRS,
    CONF_STOP_NAME,
    CONF_STOP_NUMBER,
    DOMAIN,
    decode_pair,
)
from .coordinator import ZditmCoordinator
from .times import compute_minutes, is_live


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for one stop."""
    coordinator = hass.data[DOMAIN]["entries"][entry.entry_id]
    entities: list[SensorEntity] = [StopNextDepartureSensor(coordinator, entry)]
    for encoded in entry.options.get(CONF_PAIRS, []):
        line, direction = decode_pair(encoded)
        entities.append(LineDirectionSensor(coordinator, entry, line, direction))
    async_add_entities(entities)


class _ZditmBase(CoordinatorEntity, SensorEntity):
    """Shared base for ZDiTM sensor entities."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator: ZditmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._stop_number: str = entry.data[CONF_STOP_NUMBER]
        self._stop_name: str = entry.data[CONF_STOP_NAME]

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._stop_number)},
            name=self._stop_name,
            manufacturer="ZDiTM Szczecin",
            model="Przystanek",
        )


class StopNextDepartureSensor(_ZditmBase):
    """Minutes to the next departure at the stop; full list in attributes."""

    _attr_name = "Następny odjazd"

    def __init__(self, coordinator: ZditmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_stop_{self._stop_number}"

    @property
    def native_value(self) -> int | None:
        deps = (self.coordinator.data or {}).get("departures", [])
        if not deps:
            return None
        return compute_minutes(deps[0]["time_real"], deps[0]["time_scheduled"], dt_util.now())

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        now = dt_util.now()
        return {
            "stop_name": data.get("stop_name"),
            "stop_number": data.get("stop_number"),
            "message": data.get("message"),
            "updated_at": data.get("updated_at"),
            "departures": [
                {
                    "line": d["line"],
                    "direction": d["direction"],
                    "minutes": compute_minutes(d["time_real"], d["time_scheduled"], now),
                    "is_live": is_live(d["time_real"]),
                    "time_scheduled": d["time_scheduled"],
                    "category": d["category"],
                }
                for d in data.get("departures", [])
            ],
        }


class LineDirectionSensor(_ZditmBase):
    """Minutes to the next departure of one (line, direction) pair."""

    def __init__(
        self, coordinator: ZditmCoordinator, entry: ConfigEntry, line: str, direction: str
    ) -> None:
        super().__init__(coordinator, entry)
        self._line = line
        self._direction = direction
        self._attr_name = f"{line} → {direction}"
        self._attr_unique_id = f"{entry.entry_id}_{self._stop_number}_{line}_{direction}"

    def _match(self) -> dict | None:
        for d in (self.coordinator.data or {}).get("departures", []):
            if str(d["line"]) == str(self._line) and d["direction"] == self._direction:
                return d
        return None

    @property
    def native_value(self) -> int | None:
        d = self._match()
        if d is None:
            return None
        return compute_minutes(d["time_real"], d["time_scheduled"], dt_util.now())

    @property
    def extra_state_attributes(self) -> dict:
        d = self._match()
        return {
            "line": self._line,
            "direction": self._direction,
            "is_live": is_live(d["time_real"]) if d else False,
            "time_scheduled": d["time_scheduled"] if d else None,
            "category": d["category"] if d else None,
        }
