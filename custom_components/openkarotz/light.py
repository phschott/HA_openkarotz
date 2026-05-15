from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"


LIGHTS = [
    (
        "1",
        "color_1",
    ),
    (
        "2",
        "color_2",
    ),
]


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities = [
        KarotzColorLight(
            coordinator,
            suffix,
            translation_key,
        )
        for (
            suffix,
            translation_key,
        ) in LIGHTS
    ]

    async_add_entities(entities)


class KarotzBaseLight(
    CoordinatorEntity,
    LightEntity,
):
    _attr_has_entity_name = True

    device_id: str
    device_name: str

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.device_id)
            },
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }


class KarotzColorLight(
    KarotzBaseLight,
):

    device_id = "karotz_leds"
    device_name = "OpenKarotz LEDs"

    _attr_color_mode = (
        ColorMode.RGB
    )

    _attr_supported_color_modes = {
        ColorMode.RGB
    }

    def __init__(
        self,
        coordinator,
        suffix,
        translation_key,
    ):
        super().__init__(coordinator)

        self.suffix = suffix

        self.entity_id = (
            f"light.openkarotz_color_{suffix}"
        )

        self._attr_translation_key = (
            translation_key
        )

        self._attr_unique_id = (
            f"openkarotz_color_{suffix}"
        )

        self._attr_rgb_color = (
            0,
            255,
            0,
        )

        self._attr_is_on = True

    async def async_turn_on(
        self,
        **kwargs,
    ):

        rgb_color = kwargs.get(
            "rgb_color"
        )

        if rgb_color is not None:
            self._attr_rgb_color = (
                rgb_color
            )

        self._attr_is_on = True

        self.async_write_ha_state()

    async def async_turn_off(
        self,
        **kwargs,
    ):

        self._attr_is_on = False

        self.async_write_ha_state()
