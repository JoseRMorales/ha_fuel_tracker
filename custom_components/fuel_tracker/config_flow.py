"""Adds config flow for Fuel Tracker."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import voluptuous as vol
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)

from .const import CONF_NAME, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Mapping

CONFIG_SCHEMA = vol.Schema({vol.Required(CONF_NAME): selector.TextSelector()})

CONFIG_FLOW = {"user": SchemaFlowFormStep(CONFIG_SCHEMA)}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config flow for Fuel Tracker integration."""

    VERSION = 1

    config_flow = CONFIG_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast("str", options[CONF_NAME])
