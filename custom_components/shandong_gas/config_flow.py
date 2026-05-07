from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_ORG_ID,
    CONF_REFRESH_TOKEN,
    CONF_SUBS_CODE,
    CONF_SUBS_ID,
    DOMAIN,
)
from .coordinator import ShandongGasApiClient, ShandongGasAuthError, ShandongGasApiError


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REFRESH_TOKEN): str,
        vol.Required(CONF_ACCESS_TOKEN): str,
        vol.Required(CONF_SUBS_ID): str,
        vol.Required(CONF_ORG_ID): str,
        vol.Required(CONF_SUBS_CODE): str,
    }
)


class ShandongGasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, str] | None = None) -> FlowResult:
        errors = {}

        if user_input is not None:
            session = aiohttp_client.async_get_clientsession(self.hass)
            api = ShandongGasApiClient(
                session,
                user_input[CONF_ACCESS_TOKEN],
                user_input[CONF_REFRESH_TOKEN],
                user_input[CONF_ORG_ID],
                user_input[CONF_SUBS_ID],
            )
            try:
                result = await api.async_get_data()
            except ShandongGasAuthError:
                errors["base"] = "invalid_auth"
            except ShandongGasApiError:
                errors["base"] = "cannot_connect"
            else:
                entry_data = {
                    CONF_REFRESH_TOKEN: result["refresh_token"],
                    CONF_ACCESS_TOKEN: result["access_token"],
                    CONF_SUBS_ID: user_input[CONF_SUBS_ID],
                    CONF_ORG_ID: user_input[CONF_ORG_ID],
                    CONF_SUBS_CODE: user_input[CONF_SUBS_CODE],
                }
                return self.async_create_entry(
                    title=f"{user_input[CONF_SUBS_CODE]} ({user_input[CONF_ORG_ID]})",
                    data=entry_data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
