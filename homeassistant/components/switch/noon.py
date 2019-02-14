"""
Support for Noon Home spaces (rooms).
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.noon/
"""
import logging
import voluptuous as vol

from homeassistant.components.switch import (
    SwitchDevice)
from custom_components.noon import (
    HASSNoonEntity, NOON_ENTITIES, NOON_CONTROLLER)
from homeassistant.const import ATTR_ENTITY_ID
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# TODO: Add pynoon
DEPENDENCIES = ['noon']
ATTR_SCENE_NAME = "scene_name"
ATTR_SCENE_ACTIVE = "active"

NOON_SCENE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Optional(ATTR_SCENE_NAME): vol.All(str, vol.Length(min=1)),
    vol.Optional(ATTR_SCENE_ACTIVE): bool,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    
    """ Debug """
    _LOGGER.debug("Initialising Noon Spaces...")
    
    """Set up the Noon spaces."""
    spaces = []
    for (id, space) in hass.data[NOON_CONTROLLER].spaces.items():
        _LOGGER.debug("Attempting to initialise space - {}: {}".format(id, space))
        space = HASSNoonSpace(space, hass.data[NOON_CONTROLLER])
        spaces.append(space)

    add_entities(spaces, True)


class HASSNoonSpace(HASSNoonEntity, SwitchDevice):

    """Representation of a Lutron Light, including dimmable."""

    def __init__(self, noon_device, controller):

        """Initialize the switch."""
        super().__init__(noon_device, controller)

    @property
    def name(self):
        """Return the name of the device."""
        return self._noon_device.name

    def turn_on(self, **kwargs):

        """Turn the space's scene on."""
        self._noon_device.activateScene()

    def turn_off(self, **kwargs):

        """Turn the space's scene off."""
        self._noon_device.deactivateScene()

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {}
        attr['Scene'] = self._noon_device.activeSceneName
        return attr

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._noon_device.lightsOn

    def update(self):
        """Call when forcing a refresh of the device."""
        pass