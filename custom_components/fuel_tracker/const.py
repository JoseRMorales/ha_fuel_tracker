"""Constants for the Fuel Tracker integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "fuel_tracker"
CONF_NAME = "name"
CONF_COST = "cost"
CONF_FUEL = "fuel"

SERVICE_RESET = "reset"
SERVICE_CALIBRATE = "calibrate"
SERVICE_REFUEL = "refuel"
SERVICE_ROLLBACK = "rollback"
