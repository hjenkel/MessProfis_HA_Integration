"""API client for the MessProfis Mieterportal endpoint."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import LOGIN_URL


class MessProfisApiError(Exception):
    """Base API exception."""


class MessProfisAuthError(MessProfisApiError):
    """Authentication failed."""


class MessProfisFormatError(MessProfisApiError):
    """Unexpected response format."""


class MessProfisApiClient:
    """Small API client for the portal login/data endpoint."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_fetch_raw(self, email: str, password_hash: str) -> list[dict[str, Any]]:
        """Fetch raw payload list from endpoint."""
        payload = {
            "Mail": email,
            "PasswordHash": password_hash,
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://mieterportal.mess-profis.de",
            "Referer": "https://mieterportal.mess-profis.de/login",
        }

        try:
            response = await self._session.post(
                LOGIN_URL,
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            data = await response.json()
        except ClientResponseError as err:
            if err.status in (401, 403):
                raise MessProfisAuthError("Authentication failed") from err
            raise MessProfisApiError(f"HTTP error while requesting API: {err.status}") from err
        except (ClientError, TimeoutError) as err:
            raise MessProfisApiError("Network error while requesting API") from err
        except ValueError as err:
            raise MessProfisFormatError("Response body is not valid JSON") from err

        if not isinstance(data, list):
            raise MessProfisFormatError("Unexpected API response format, expected list")
        if not all(isinstance(item, dict) for item in data):
            raise MessProfisFormatError("Unexpected API response format, expected list of objects")

        return data
