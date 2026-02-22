"""Config flow for MessProfis Mieterportal."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MessProfisApiClient, MessProfisApiError, MessProfisAuthError
from .const import (
    CONF_PASSWORD_HASH,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    MAX_UPDATE_INTERVAL_HOURS,
    MIN_UPDATE_INTERVAL_HOURS,
)


async def _validate_credentials(
    hass: HomeAssistant, email: str, password_hash: str
) -> None:
    """Validate credentials against the endpoint."""
    client = MessProfisApiClient(async_get_clientsession(hass))
    await client.async_fetch_raw(email=email, password_hash=password_hash)


class MessProfisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MessProfis Mieterportal."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = str(user_input[CONF_EMAIL]).strip().lower()
            password_hash = str(user_input[CONF_PASSWORD_HASH]).strip()

            await self.async_set_unique_id(email)
            self._abort_if_unique_id_configured()

            try:
                await _validate_credentials(self.hass, email, password_hash)
            except MessProfisAuthError:
                errors["base"] = "invalid_auth"
            except MessProfisApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # pragma: no cover - defensive fallback
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=email,
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD_HASH: password_hash,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD_HASH): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "MessProfisOptionsFlow":
        """Create the options flow."""
        return MessProfisOptionsFlow(config_entry)


class MessProfisOptionsFlow(config_entries.OptionsFlow):
    """Handle options for MessProfis Mieterportal."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_hours = int(
            self._config_entry.options.get(
                CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
            )
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_INTERVAL_HOURS,
                    default=current_hours,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_UPDATE_INTERVAL_HOURS, max=MAX_UPDATE_INTERVAL_HOURS
                    ),
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
