"""Constants for the homekit_controller component."""
DOMAIN = "homekit_controller"

KNOWN_DEVICES = f"{DOMAIN}-devices"
CONTROLLER = f"{DOMAIN}-controller"
ENTITY_MAP = f"{DOMAIN}-entity-map"
ENTITY_REGISTRATION = f"{DOMAIN}-entity-registration"

HOMEKIT_DIR = ".homekit"
PAIRING_FILE = "pairing.json"

SERVICE_HOMEKITCONTROLLER_SET_CUSTOM = "set_custom_characteristic"
ATTR_CHARACTERISTIC_ID = "char_name"
ATTR_CHARACTERISTIC_VALUE = "char_value"

# Mapping from Homekit type to component.
HOMEKIT_ACCESSORY_DISPATCH = {
    "lightbulb": "light",
    "outlet": "switch",
    "switch": "switch",
    "thermostat": "climate",
    "security-system": "alarm_control_panel",
    "garage-door-opener": "cover",
    "window": "cover",
    "window-covering": "cover",
    "lock-mechanism": "lock",
    "contact": "binary_sensor",
    "motion": "binary_sensor",
    "carbon-dioxide": "sensor",
    "humidity": "sensor",
    "light": "sensor",
    "temperature": "sensor",
    "battery": "sensor",
    "smoke": "binary_sensor",
    "fan": "fan",
    "fanv2": "fan",
    "air-quality": "air_quality",
}
