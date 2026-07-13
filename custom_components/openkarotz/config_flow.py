"""Config flow for the OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

DOMAIN = "openkarotz"


class KarotzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenKarotz."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Karotz",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("host"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
