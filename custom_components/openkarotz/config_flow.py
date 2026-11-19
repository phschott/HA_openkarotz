"""Config flow for the OpenKarotz integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .api import KarotzAPI
from .const import CONF_NAME, DEFAULT_KAROTZ_NAME, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"


class KarotzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenKarotz."""

    # 2: unique_ids and device identifiers are scoped per config entry.
    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input[CONF_NAME].strip() or DEFAULT_KAROTZ_NAME
            api = KarotzAPI(host, async_get_clientsession(self.hass))
            try:
                status = await api.get_status()
            except Exception:
                _LOGGER.debug("Cannot reach Karotz at %s", host, exc_info=True)
                errors["base"] = "cannot_connect"
            else:
                mac = status.get("wlan_mac") if isinstance(status, dict) else None
                if mac:
                    # Same rabbit at a new IP: just update the host.
                    await self.async_set_unique_id(format_mac(mac))
                    self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                else:
                    self._async_abort_entries_match({CONF_HOST: host})
                return self.async_create_entry(
                    title=name,
                    data={CONF_HOST: host, CONF_NAME: name},
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED)
                ): str,
                vol.Required(
                    CONF_NAME,
                    default=(user_input or {}).get(CONF_NAME, DEFAULT_KAROTZ_NAME),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
