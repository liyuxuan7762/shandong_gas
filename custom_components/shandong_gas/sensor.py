from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import CoordinatorEntity
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN
from .coordinator import ShandongGasDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: ShandongGasDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            ShandongGasBalanceSensor(coordinator, entry),
            ShandongGasLastReadingDateSensor(coordinator, entry),
        ],
        True,
    )


class ShandongGasBalanceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: ShandongGasDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Balance"
        self._attr_unique_id = f"{entry.entry_id}_available_balance"
        self._attr_native_unit_of_measurement = "CNY"
        self._attr_icon = "mdi:currency-cny"
        self._entry = entry

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("available_balance")

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        return {
            "org_id": self._entry.data.get("org_id"),
            "subs_id": self._entry.data.get("subs_id"),
            "subs_code": self._entry.data.get("subs_code"),
        }


class ShandongGasLastReadingDateSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: ShandongGasDataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Last Meter Reading"
        self._attr_unique_id = f"{entry.entry_id}_last_meter_reading_date"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get("last_meter_reading_date")
