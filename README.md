# Fuel Tracker Home Assistant Integration

Track your vehicle's fuel usage and costs directly in Home Assistant! This integration provides sensors and services to help you monitor refueling, calibrate values, reset, and roll back changes, making it easy to keep tabs on your fuel consumption and spending.

## Features
- **Fuel and Cost Tracking:** Monitors total fuel added and total cost.
- **History and Rollback:** Keeps a history of changes for both sensors, allowing you to roll back to previous values.
- **Services:**
  - `refuel`: Add new fuel and/or cost entries.
  - `calibrate`: Set sensors to a specific value.
  - `reset`: Reset sensors to zero.
  - `rollback`: Undo the last change.
- **Configurable via UI:** Set up and manage the integration through Home Assistant’s UI.

## Installation

### HACS (Recommended)
1. Go to HACS > Integrations > Custom Repositories.
2. Add this repository: `https://github.com/JoseRMorales/ha_fuel_tracker` as an integration.
3. Install **Fuel Tracker** from HACS.
4. Restart Home Assistant.

### Manual
1. Copy the `custom_components/fuel_tracker` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration
Fuel Tracker is a helper integration so installation is made from the `helpers` section in Home Assistant.
1. In Home Assistant, go to **Settings > Devices & Services > Helpers**.
2. Add a new helper.
2. Search for **Fuel Tracker** and follow the prompts to set it up.

## Entities
- `sensor.fuel_tracker`: Tracks total fuel added (liters).
- `sensor.cost_tracker`: Tracks total fuel cost (EUR).

## Services
You can call these services from Developer Tools > Services or in automations/scripts:

- `fuel_tracker.refuel`: Add a refuel event.
  - `fuel` (required): Amount of fuel added (liters).
  - `cost` (required): Cost of the refuel (EUR).
- `fuel_tracker.calibrate`: Set the sensors to a specific value.
  - `fuel` (optional): Set fuel sensor to this value.
  - `cost` (optional): Set cost sensor to this value.
- `fuel_tracker.reset`: Reset sensors to zero.
- `fuel_tracker.rollback`: Roll back to the previous value.

## Example Service Call (YAML)
```yaml
service: fuel_tracker.refuel
data:
  entity_id: sensor.fuel_tracker
  fuel: "40"
  cost: "60"
```

## State Attributes
Each sensor provides:
- `history_size`: Number of previous values stored.
- `can_rollback`: Whether rollback is available.

## Support
- [GitHub Issues](https://github.com/JoseRMorales/ha_fuel_tracker/issues)

## Contributing
Pull requests are welcome! Please open an issue first to discuss major changes.

## License
[MIT License](LICENSE)
