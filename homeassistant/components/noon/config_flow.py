"""Config flow for Noon Home integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import aiohttp_client

from .aiopynoon import Noon
from .aiopynoon.exceptions import NoonAuthenticationError
from .const import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Noon Home."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:

                session = aiohttp_client.async_get_clientsession(self.hass)
                noon = Noon(
                    session, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )

                if await noon.authenticate():
                    return self.async_create_entry(
                        title=user_input[CONF_USERNAME], data=user_input
                    )

            except NoonAuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
