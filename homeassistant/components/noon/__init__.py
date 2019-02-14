import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.discovery import load_platform
from homeassistant.const import ATTR_ENTITY_ID
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.service import extract_entity_ids
from homeassistant.helpers.entity_component import EntityComponent

REQUIREMENTS = ['pynoon==0.0.15']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'noon'
NOON_CONTROLLER = 'noon_controller'
NOON_ENTITIES = 'noon_entities'

ATTR_SCENE_NAME = "scene_name"
ATTR_SCENE_ACTIVE = "active"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

NOON_SCENE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required(ATTR_SCENE_NAME): vol.All(str, vol.Length(min=1)),
    vol.Optional(ATTR_SCENE_ACTIVE): bool,
})


def setup(hass, hass_config):

    # pip3 install git+https://github.com/alistairg/pynoon
    from pynoon import Noon

    component = EntityComponent(_LOGGER, DOMAIN, hass)

    def handle_set_scene(call):
        """ Set the given room director to a specific scene """
        sceneName = call.data.get(ATTR_SCENE_NAME)
        sceneActive = call.data.get(ATTR_SCENE_ACTIVE, None)
        component = hass.data[DOMAIN]
        entityIds = call.data.get(ATTR_ENTITY_ID)
        for entityId in entityIds:
            entity = component.get_entity(entityId)
            if isinstance(entity, HASSNoonRoomDirector):
                entity.setScene(sceneName, active=sceneActive)
            elif entity is None:
                _LOGGER.error("Didn't get an entity to control")
            else:
                _LOGGER.error("Entity {} is not a Noon Room Director ({})"
                              .format(entity.name, entity.__class__.__name__))

    """ Initialise storage """
    config = hass_config.get(DOMAIN)
    hass.data[NOON_ENTITIES] = {
        'line': [],
        'space': []
    }

    """ Initialise PyNoon """
    _LOGGER.info("Initialising Noon Home with user '{}'..."
                 .format(config[CONF_USERNAME]))
    hass.data[NOON_CONTROLLER] = Noon(config[CONF_USERNAME],
                                      config[CONF_PASSWORD])

    """ Attempt to login """
    try:
        hass.data[NOON_CONTROLLER].authenticate()
    except:
        _LOGGER.error("Noon authentication failed.")
        return

    """ Attempt to get devices """
    try:
        hass.data[NOON_CONTROLLER].discoverDevices()
    except:
        _LOGGER.error("Noon device discovery failed.")
        return

    """ Load lines """
    load_platform(hass, 'light', DOMAIN, None, hass_config)

    """ Load space switches """
    load_platform(hass, 'switch', DOMAIN, None, hass_config)

    """Set up the Noon spaces."""
    roomDirectors = []
    for (id, space) in hass.data[NOON_CONTROLLER].spaces.items():
        _LOGGER.debug("Attempting to initialise space - {}: {}"
                      .format(id, space))
        roomDirector = HASSNoonRoomDirector(space, hass.data[NOON_CONTROLLER])
        roomDirectors.append(roomDirector)
    component.add_entities(roomDirectors)
    hass.data[DOMAIN] = component

    """ Register the set-scene service """
    hass.services.register("noon", "set_scene", handle_set_scene,
                           schema=NOON_SCENE_SCHEMA)

    """ Listen for changes """
    hass.data[NOON_CONTROLLER].connect()

    """ Success """
    return True


class HASSNoonEntity(Entity):

    def __init__(self, noon_device, controller):

        """Initialize the device."""
        self._noon_device = noon_device
        self._controller = controller

    @property
    def unique_id(self):
        """Return the unique id of the device."""
        return self._noon_device.guid

    @property
    def name(self):
        """Return the name of the device."""
        return self._noon_device.name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    async def async_added_to_hass(self):
        """Register callbacks."""
        self.hass.async_add_executor_job(
            self._noon_device.subscribe,
            self._update_callback,
            None
        )

    def _update_callback(self, _device, _context, _event, _params):
        """Run when invoked by pynoon when the device state changes."""
        _LOGGER.debug("Got update notification for Noon device '{}'"
                      .format(self.name))
        self.schedule_update_ha_state()


class HASSNoonRoomDirector(HASSNoonEntity, Entity):

    """Representation of a Lutron Light, including dimmable."""

    def __init__(self, noon_device, controller):

        """Initialize the entity."""
        super().__init__(noon_device, controller)

        """Set an initial state"""
        _LOGGER.error("My entity id is {}".format(self.entity_id))

    @property
    def name(self):
        """Return the name of the device."""
        return self._noon_device.name

    @property
    def state_attributes(self):
        """Return the state attributes."""
        attr = {}
        attr['Scene'] = self._noon_device.activeSceneName
        attr['Lights On'] = self._noon_device.lightsOn
        return attr

    @property
    def state(self):
        return self._noon_device.activeSceneName

    def update(self):
        """Call when forcing a refresh of the device."""
        _LOGGER.error("UPDATE() called on '{}'".format(self.name))
        pass

    def setScene(self, sceneName, active=None):
        _LOGGER.debug("Setting scene for {} to {}..."
                      .format(self.name, sceneName))
        self._noon_device.setSceneActive(sceneIdOrName=sceneName, active=active)