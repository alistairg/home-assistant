"""The Noon Home integration."""
import asyncio
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client

from .aiopynoon import Noon
from .aiopynoon.exceptions import NoonAuthenticationError
from .const import DATA_NOON, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["light", "switch"]


async def async_setup_noon(hass: HomeAssistant, config):
    """Set up the Noon Home component."""

    entry_id = config.entry_id
    session = aiohttp_client.async_get_clientsession(hass)
    _LOGGER.debug(f"Initializing with {config}...")
    noon = Noon(session, config.data[CONF_USERNAME], config.data[CONF_PASSWORD])

    # Authenticate
    try:
        await noon.authenticate()
    except NoonAuthenticationError:
        _LOGGER.error("Password is no longer valid. Please set up Noon again.")
        return False

    # Store root connection
    hass.data[DOMAIN][entry_id][DATA_NOON] = noon
    _LOGGER.debug("Authenticated successfully with Noon. Proceeding...")

    # Pre-load lines and spaces
    lines = await noon.lines
    spaces = await noon.spaces
    _LOGGER.debug(
        "Initialized Noon with {} spaces, and {} lines".format(len(spaces), len(lines))
    )

    # Setup platforms
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config, component)
        )

    # Open the event stream
    await noon.open_eventstream()

    # Done
    return True


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the domain."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Noon Home from a config entry."""

    _LOGGER.debug(f"Setting up noon from config entry {entry}")
    hass.data[DOMAIN][entry.entry_id] = {}

    try:
        return await async_setup_noon(hass, entry)
    except asyncio.TimeoutError:
        raise ConfigEntryNotReady


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    noon = hass.data[DOMAIN][entry.entry_id][DATA_NOON]
    await noon.close_eventstream()

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
