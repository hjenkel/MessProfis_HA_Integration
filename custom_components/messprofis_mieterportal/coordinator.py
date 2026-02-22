"""Coordinator for MessProfis data updates."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MessProfisApiClient, MessProfisApiError, MessProfisAuthError
from .const import (
    CONF_PASSWORD_HASH,
    CONF_UPDATE_INTERVAL_HOURS,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
)
from .models import ApartmentReading
from .parser import extract_apartment_readings

_LOGGER = logging.getLogger(__name__)


class MessProfisDataUpdateCoordinator(DataUpdateCoordinator[list[ApartmentReading]]):
    """Handle periodic data refresh from MessProfis endpoint."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        update_hours = config_entry.options.get(
            CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS
        )
        update_interval = timedelta(hours=int(update_hours))

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self._email = str(config_entry.data["email"])
        self._password_hash = str(config_entry.data[CONF_PASSWORD_HASH])
        self._client = MessProfisApiClient(async_get_clientsession(hass))

    async def _async_update_data(self) -> list[ApartmentReading]:
        """Fetch data from API and normalize it."""
        try:
            payload = await self._client.async_fetch_raw(self._email, self._password_hash)
            return extract_apartment_readings(payload)
        except MessProfisAuthError as err:
            raise ConfigEntryAuthFailed("Authentication with MessProfis failed") from err
        except MessProfisApiError as err:
            raise UpdateFailed(f"MessProfis update failed: {err}") from err
