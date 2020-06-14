"""Support for Noon room director."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity

from .const import ATTR_AVAILABLE_SCENES, ATTR_CURRENT_SCENE, DATA_NOON, DOMAIN
from .entity import NoonEntityMixin

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Noon room directors."""
    noon = hass.data[DOMAIN][config_entry.entry_id][DATA_NOON]
    spaces = await noon.spaces
    entities = []

    for room_director in spaces.values():
        _LOGGER.debug("Adding room director for for %s", room_director.name)
        entities.append(NoonRoomDirector(noon, room_director))

    async_add_entities(entities, True)


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
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the selected scene."""
        return await self._room_director.activate_scene()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the selected scene."""
        return await self._room_director.deactivate_scene()
