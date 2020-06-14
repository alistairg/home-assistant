"""Base class for Noon entity."""

import logging

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


class NoonEntityMixin(Entity):
    """Base implementation for Noon device."""

    def __init__(self, noon, entity):
        """Initialize an August device."""
        super().__init__()
        self._noon = noon
        self._noon_entity = entity

    @property
    def should_poll(self):
        """Return False, updates are controlled via the hub."""
        return False

    @property
    def name(self):
        """Return the name of this device."""
        return self._noon_entity.name

    @property
    def available(self):
        """Return the availability of this sensor."""
        return True
        return self._noon.event_stream_connected

    async def _noon_entity_changed(self, noon, entity, change_type, change):
        _LOGGER.debug("Entity changed!")
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        _LOGGER.debug("Subscribing to updates!")
        self._noon_entity.subscribe(self._noon_entity_changed, None)

    async def async_will_remove_from_hass(self):
        """Undo subscription."""
        _LOGGER.debug("Stopping subscription.")
        self._noon_entity.unsubscribe(self._noon_entity_changed, None)

    @property
    def unique_id(self) -> str:
        """Get the unique id of the entity."""
        return f"{self._noon_entity.guid}"
