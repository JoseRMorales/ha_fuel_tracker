"""Adds config flow for Fuel Tracker."""

from __future__ import annotations

from decimal import Decimal

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_COST,
    CONF_DEVICE_TYPE,
    CONF_FUEL,
    CONF_NAME,
    DEVICE_TYPE_EV,
    DEVICE_TYPE_FUEL,
    DEVICE_TYPE_WEIGHT,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_DEVICE_TYPE, default=DEVICE_TYPE_FUEL): SelectSelector(
            SelectSelectorConfig(
                options=[DEVICE_TYPE_FUEL, DEVICE_TYPE_EV, DEVICE_TYPE_WEIGHT],
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="device_type",
            )
        ),
        vol.Optional(CONF_COST, default="0"): str,
        vol.Optional(CONF_FUEL, default="0"): str,
    }
)


class FuelTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fuel Tracker."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        if user_input is not None:
            for key in (CONF_COST, CONF_FUEL):
                try:
                    Decimal(str(user_input.get(key, "0")))
                except Exception:  # noqa: BLE001
                    errors[key] = "invalid_number"
            if not errors:
                await self.async_set_unique_id(user_input[CONF_NAME])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_DEVICE_TYPE: user_input[CONF_DEVICE_TYPE],
                        CONF_COST: user_input.get(CONF_COST),
                        CONF_FUEL: user_input.get(CONF_FUEL),
                    },
                )
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
