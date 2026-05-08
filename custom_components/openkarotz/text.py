from homeassistant.components.text import TextEntity

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    async_add_entities(
        [
            KarotzTTSText(coordinator),
        ]
    )


class KarotzTTSText(TextEntity):

    def __init__(self, coordinator):

        self.coordinator = coordinator

        self._attr_name = "Karotz TTS"

        self._attr_unique_id = (
            "openkarotz_tts"
        )

        self._attr_icon = (
            "mdi:text-box"
        )

        self._attr_native_value = ""

    async def async_set_value(
        self,
        value,
    ):
        self._attr_native_value = value

        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz_sound")
            },
            "name": "OpenKarotz Sound",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }
