import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "openkarotz"

class KarotzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Karotz",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("host"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
