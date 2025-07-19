"""Fuel Tracker sensors."""

from collections import deque
from decimal import Decimal
from typing import Any

import voluptuous as vol
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.template import is_number

from .const import (
    CONF_COST,
    CONF_FUEL,
    LOGGER,
    SERVICE_CALIBRATE,
    SERVICE_REFUEL,
    SERVICE_RESET,
    SERVICE_ROLLBACK,
)

MAX_HISTORY_SIZE = 10


class FuelTrackerValidationError(vol.Invalid):
    """Custom validation error for Fuel Tracker sensor values."""

    def __init__(self, value: Any, reason: str) -> None:
        """Initialize FuelTrackerValidationError with the invalid value and reason."""
        msg = f"Value '{value}' is invalid: {reason}"
        super().__init__(msg)


def validate_number(value: Any) -> str:
    """Validate value is a number and is greater than 0."""
    if not is_number(value):
        msg = "Value is not a number"
        raise FuelTrackerValidationError(value, msg)
    if Decimal(value) <= 0:
        msg = "Value is not greater than 0"
        raise FuelTrackerValidationError(value, msg)
    return value


async def async_setup_entry(
    _: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize sensors for Fuel Tracker from a config entry."""
    entry_name = config_entry.title
    entry_id = config_entry.entry_id

    cost_tracker_sensor = CostTrackerSensor(entry_name, entry_id)
    fuel_tracker_sensor = FuelTrackerSensor(entry_name, entry_id)
    async_add_entities([cost_tracker_sensor, fuel_tracker_sensor])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_REFUEL,
        {
            vol.Required(CONF_COST): validate_number,
            vol.Required(CONF_FUEL): validate_number,
        },
        "async_refuel",
    )
    platform.async_register_entity_service(
        SERVICE_CALIBRATE,
        {
            vol.Optional(CONF_COST): validate_number,
            vol.Optional(CONF_FUEL): validate_number,
        },
        "async_calibrate",
    )
    platform.async_register_entity_service(
        SERVICE_RESET,
        {},
        "async_reset",
    )
    platform.async_register_entity_service(
        SERVICE_ROLLBACK,
        {},
        "async_rollback",
    )


class CostTrackerSensor(RestoreSensor):
    """Representation of a Cost sensor."""

    _attr_translation_key = "cost_tracker"
    _attr_should_poll = False
    _attr_native_unit_of_measurement = "EUR"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_has_entity_name = True

    def __init__(self, name: str, unique_id: str) -> None:
        """Initialize the cost tracker sensor."""
        self._attr_unique_id = f"{unique_id}_{CONF_COST}"
        self._attr_native_value = Decimal("0.0")
        self._value_history = deque(maxlen=MAX_HISTORY_SIZE)
        self.translation_placeholders = {
            "name": name,
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity being added to Home Assistant."""
        await super().async_added_to_hass()

    def _store_current_value(self) -> None:
        """Store the current value in history before making changes."""
        if self._attr_native_value is not None:
            self._value_history.append(self._attr_native_value)
            LOGGER.debug(
                "Stored value %s in history. History size: %d",
                self._attr_native_value,
                len(self._value_history),
            )

    async def async_reset(self) -> None:
        """Reset the sensor state."""
        self._store_current_value()
        self._attr_native_value = Decimal("0.0")
        self.async_write_ha_state()

    async def async_refuel(self, _: str | None = None, cost: str | None = None) -> None:
        """Update the sensor state."""
        if not cost:
            msg = "Cost is required for cost refuel"
            raise HomeAssistantError(msg)
        self._store_current_value()
        current_value = self._attr_native_value
        if not isinstance(current_value, Decimal):
            try:
                current_value = Decimal(str(current_value))
            except ValueError:
                current_value = Decimal("0.0")
        self._attr_native_value = current_value + Decimal(cost)
        self.async_write_ha_state()

    async def async_calibrate(
        self, _: str | None = None, cost: str | None = None
    ) -> None:
        """Update the sensor state."""
        if not cost:
            msg = "Cost is required for cost calibration"
            raise HomeAssistantError(msg)
        self._store_current_value()
        self._attr_native_value = Decimal(cost)
        self.async_write_ha_state()

    async def async_rollback(self) -> None:
        """Rollback the sensor state to the previous value."""
        if len(self._value_history) == 0:
            LOGGER.warning("No history available for rollback")
            msg = "No history available for rollback"
            raise HomeAssistantError(msg)

        previous_value = self._value_history.pop()

        LOGGER.info(
            "Rolling back cost from %s to %s. Remaining history: %d",
            self._attr_native_value,
            previous_value,
            len(self._value_history),
        )

        self._attr_native_value = previous_value
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        return {
            "history_size": len(self._value_history),
            "can_rollback": len(self._value_history) > 0,
        }


class FuelTrackerSensor(RestoreSensor):
    """Representation of a fuel sensor."""

    _attr_translation_key = "fuel_tracker"
    _attr_should_poll = False
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_value = Decimal("0.0")
    _attr_icon = "mdi:gas-station"
    _attr_has_entity_name = True

    def __init__(self, name: str, entry_id: str) -> None:
        """Initialize the fuel tracker sensor."""
        self._attr_unique_id = f"{entry_id}_{CONF_FUEL}"
        self._value_history = deque(maxlen=MAX_HISTORY_SIZE)
        self.translation_placeholders = {
            "name": name,
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

    def _store_current_value(self) -> None:
        """Store the current value in history before making changes."""
        if self._attr_native_value is not None:
            self._value_history.append(self._attr_native_value)
            LOGGER.debug(
                "Stored value %s in history. History size: %d",
                self._attr_native_value,
                len(self._value_history),
            )

    async def async_reset(self) -> None:
        """Reset the sensor state."""
        self._store_current_value()
        self._attr_native_value = Decimal("0.0")
        self.async_write_ha_state()

    async def async_refuel(self, fuel: str | None = None, _: str | None = None) -> None:
        """Update the sensor state."""
        if not fuel:
            msg = "Fuel is required for fuel refuel"
            raise HomeAssistantError(msg)
        self._store_current_value()
        current_value = self._attr_native_value
        if not isinstance(current_value, Decimal):
            try:
                current_value = Decimal(str(current_value))
            except ValueError:
                current_value = Decimal("0.0")
        self._attr_native_value = current_value + Decimal(fuel)
        self.async_write_ha_state()

    async def async_calibrate(
        self, fuel: str | None = None, _: str | None = None
    ) -> None:
        """Update the sensor state."""
        if not fuel:
            msg = "Fuel is required for fuel calibration"
            raise HomeAssistantError(msg)
        self._store_current_value()
        self._attr_native_value = Decimal(fuel)
        self.async_write_ha_state()

    async def async_rollback(self) -> None:
        """Rollback the sensor state to the previous value."""
        if len(self._value_history) == 0:
            LOGGER.warning("No history available for rollback")
            msg = "No history available for rollback"
            raise HomeAssistantError(msg)

        previous_value = self._value_history.pop()

        LOGGER.info(
            "Rolling back fuel from %s to %s. Remaining history: %d",
            self._attr_native_value,
            previous_value,
            len(self._value_history),
        )

        self._attr_native_value = previous_value
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        return {
            "history_size": len(self._value_history),
            "can_rollback": len(self._value_history) > 0,
        }
