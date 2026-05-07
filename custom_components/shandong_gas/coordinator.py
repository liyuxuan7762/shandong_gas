from __future__ import annotations

import logging

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_BASE,
    CONF_ACCESS_TOKEN,
    CONF_ORG_ID,
    CONF_REFRESH_TOKEN,
    CONF_SUBS_ID,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class ShandongGasApiError(Exception):
    pass


class ShandongGasAuthError(ShandongGasApiError):
    pass


class ShandongGasApiClient:
    def __init__(self, session, access_token: str, refresh_token: str, org_id: str, subs_id: str):
        self._session = session
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.org_id = org_id
        self.subs_id = subs_id

    async def _get_balance(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{API_BASE}/nv1/vcc-cbs/charge/gasFeeBaseinfo?orgId={self.org_id}&subsId={self.subs_id}"

        async with self._session.get(url, headers=headers, timeout=10) as response:
            if response.status == 401:
                raise ShandongGasAuthError("access token invalid or expired")
            if response.status >= 400:
                raise ShandongGasApiError(f"Balance request failed: {response.status}")
            data = await response.json()

        if data.get("resultCode") != "0":
            raise ShandongGasAuthError("balance request returned invalid result code")

        return data

    async def _refresh_token(self) -> dict:
        url = f"{API_BASE}/vcc-oauth/oauth/authorize2/refreshToken?refreshToken={self.refresh_token}"

        async with self._session.get(url, timeout=10) as response:
            if response.status >= 400:
                raise ShandongGasAuthError("refresh token request failed")
            data = await response.json()

        if not data.get("access_token") or not data.get("refresh_token"):
            raise ShandongGasAuthError("refresh token response missing tokens")

        return data

    async def async_get_data(self) -> dict:
        try:
            data = await self._get_balance(self.access_token)
        except ShandongGasAuthError:
            refresh_data = await self._refresh_token()
            self.access_token = refresh_data["access_token"]
            self.refresh_token = refresh_data["refresh_token"]
            data = await self._get_balance(self.access_token)

        return {
            "available_balance": data.get("availableBalance"),
            "last_meter_reading_date": data.get("lastMeterReadingDate"),
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }


class ShandongGasDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, session, entry: ConfigEntry) -> None:
        self.entry = entry
        self._session = session

        super().__init__(
            hass,
            _LOGGER,
            name=entry.title,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        api = ShandongGasApiClient(
            self._session,
            self.entry.data[CONF_ACCESS_TOKEN],
            self.entry.data[CONF_REFRESH_TOKEN],
            self.entry.data[CONF_ORG_ID],
            self.entry.data[CONF_SUBS_ID],
        )

        try:
            result = await api.async_get_data()
        except (ClientError, ShandongGasApiError) as err:
            raise UpdateFailed(err) from err

        updated_data = dict(self.entry.data)
        if result["access_token"] != self.entry.data[CONF_ACCESS_TOKEN] or result["refresh_token"] != self.entry.data[CONF_REFRESH_TOKEN]:
            updated_data[CONF_ACCESS_TOKEN] = result["access_token"]
            updated_data[CONF_REFRESH_TOKEN] = result["refresh_token"]
            self.hass.config_entries.async_update_entry(self.entry, data=updated_data)

        return {
            "available_balance": result["available_balance"],
            "last_meter_reading_date": result["last_meter_reading_date"],
        }
