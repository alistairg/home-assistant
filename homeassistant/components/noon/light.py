"""Support for Noon line."""
import logging
from typing import Any

from aiopynoon.line import LINE_STATE_ON

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    SUPPORT_BRIGHTNESS,
    SUPPORT_TRANSITION,
    LightEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DATA_NOON, DOMAIN
from .entity import NoonEntityMixin

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Noon lines."""
    noon = hass.data[DOMAIN][config_entry.entry_id][DATA_NOON]
    lines = await noon.lines
    entities = []

    for line in lines.values():
        _LOGGER.debug("Adding line for %s", line.name)
        entities.append(NoonLine(noon, line))

    async_add_entities(entities, True)


class NoonLine(NoonEntityMixin, RestoreEntity, LightEntity):
    """Representation of a Noon Room Director."""

    def __init__(self, noon, line):
        """Initialize the light."""
        self._noon = noon
        self._line = line
        super().__init__(noon, line)

    @property
    def is_on(self):
        """Return the on/off state."""
        return self._line.line_state == LINE_STATE_ON

    @property
    def brightness(self):
        """Return the brightness of the line."""
        return round((self._line.dimming_level / 100.0) * 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        transition_time = None
        percentage = self._line.dimming_level
        if ATTR_TRANSITION in kwargs:
            transition_time = kwargs[ATTR_TRANSITION]
        if ATTR_BRIGHTNESS in kwargs:
            percentage = round((kwargs[ATTR_BRIGHTNESS] / 255.0) * 100.0)

        return await self._line.set_brightness(
            percentage, transition_time=transition_time
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        if ATTR_TRANSITION in kwargs:
            return await self._line.set_brightness(
                0, transition_time=kwargs[ATTR_TRANSITION]
            )
        else:
            return await self._line.turn_off()

    @property
    def supported_features(self):
        """Return the supported features of the line."""
        return SUPPORT_BRIGHTNESS | SUPPORT_TRANSITION

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {
                (DOMAIN, self._line.guid),
                (DOMAIN, self._line.parent_space.guid),
            },
            "name": self._noon_entity.name,
            "manufacturer": "Noon Home",
            "model": "Line",
        }

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        attributes = {}

        return attributes
