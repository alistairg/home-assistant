"""Support for Noon room director."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import callback
from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_AVAILABLE_SCENES,
    ATTR_CURRENT_SCENE,
    ATTR_SCENE_ACTIVE,
    ATTR_SCENE_NAME,
    DATA_NOON,
    DOMAIN,
    SVC_SET_SCENE,
)
from .entity import NoonEntityMixin

_LOGGER = logging.getLogger(__name__)

NOON_SCENE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_SCENE_NAME): vol.All(str, vol.Length(min=1)),
        vol.Optional(ATTR_SCENE_ACTIVE): bool,
    }
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Noon room directors."""
    noon = hass.data[DOMAIN][config_entry.entry_id][DATA_NOON]
    spaces = await noon.spaces
    entities = []

    for room_director in spaces.values():
        _LOGGER.debug("Adding room director for for %s", room_director.name)
        entities.append(NoonRoomDirector(noon, room_director))

    async_add_entities(entities, True)
    platform = entity_platform.current_platform.get()

    @callback
    async def async_set_scene(service_call):
        """Set the specified scene on a room director."""
        _LOGGER.error(f"Service called with params {service_call}")
        entities = await platform.async_extract_from_service(service_call)
        for entity in entities:
            hass.loop.create_task(entity.set_scene_from_service_call(service_call))

        # scene_name = call.data.get(ATTR_SCENE_NAME)
        # scene_active = call.data.get(ATTR_SCENE_ACTIVE, None)
        # all_noon_entries = hass.data[DOMAIN]
        # entity_ids = call.data.get(ATTR_ENTITY_ID)
        # for entity_id in entity_ids:
        # hass_entity = hass.
        #    for noon_entry in all_noon_entries.values():
        #        noon = noon_entry[DATA_NOON]
        #        entity = noon.get_entity(entity_id)
        #        if isinstance(entity, NoonSpace):
        #            entity.set_scene(scene_name, active=scene_active)
        #        elif entity is None:
        #            _LOGGER.error("Didn't get an entity to control")
        #        else:
        #            _LOGGER.error("Entity {} is not a Noon Room Director ({})".format(entity.name, entity.__class__.__name__))

    """Register the scene service handler."""
    hass.services.async_register(
        DOMAIN, SVC_SET_SCENE, async_set_scene, NOON_SCENE_SCHEMA
    )


class NoonRoomDirector(NoonEntityMixin, RestoreEntity, SwitchEntity):
    """Representation of a Noon Room Director."""

    def __init__(self, noon, room_director):
        """Initialize the switch."""
        self._noon = noon
        self._room_director = room_director
        super().__init__(noon, room_director)

    @property
    def is_on(self):
        """Return the on/off state."""
        return self._room_director.lights_on

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        attributes = {}

        # Active Scene
        active_scene_id = self._room_director.active_scene_id
        if active_scene_id is not None:
            active_scene = self._room_director.scenes.get(active_scene_id)
            if active_scene is not None:
                attributes[ATTR_CURRENT_SCENE] = active_scene.name
            else:
                attributes[ATTR_CURRENT_SCENE] = "Unknown"

        # Valid Scenes
        valid_scenes = []
        for scene in self._room_director.scenes.values():
            valid_scenes.append(scene.name)
        attributes[ATTR_AVAILABLE_SCENES] = ", ".join(valid_scenes)

        return attributes

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._room_director.guid)},
            "name": self._room_director.name,
            "manufacturer": "Noon Home",
            "model": "Room Director",
            "entry_type": "service",
        }

    async def set_scene_from_service_call(self, service_call):
        """Trigger a scene from a service call."""
        scene_name = service_call.data.get(ATTR_SCENE_NAME, None)
        scene_active = service_call.data.get(ATTR_SCENE_ACTIVE, None)
        _LOGGER.debug(f"Setting scene! - name {scene_name}, active {scene_active}")
        return await self._room_director.set_scene(
            scene_name=scene_name, active=scene_active
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the selected scene."""
        return await self._room_director.activate_scene()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the selected scene."""
        return await self._room_director.deactivate_scene()
