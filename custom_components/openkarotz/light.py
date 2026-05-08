from homeassistant.components.light import (
    LightEntity,
    ColorMode,
)

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
            KarotzColorLight(
                coordinator,
                "1",
                "Karotz Color 1",
            ),
            KarotzColorLight(
                coordinator,
                "2",
                "Karotz Color 2",
            ),
        ]
    )

class KarotzColorLight(LightEntity):

    def __init__(
        self,
        coordinator,
        suffix,
        name,
    ):

        self.coordinator = coordinator

        self.suffix = suffix

        self._attr_name = name

        self._attr_unique_id = (
            f"openkarotz_color_{suffix}"
        )

        self._attr_color_mode = (
            ColorMode.RGB
        )

        self._attr_supported_color_modes = {
            ColorMode.RGB
        }

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

        if "rgb_color" in kwargs:
            self._attr_rgb_color = kwargs[
                "rgb_color"
            ]

        self._attr_is_on = True

        self.async_write_ha_state()

    async def async_turn_off(
        self,
        **kwargs,
    ):
        self._attr_is_on = False

        self.async_write_ha_state()