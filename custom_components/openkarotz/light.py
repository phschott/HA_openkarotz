from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN
from .led_helper import apply_led_settings

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
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        KarotzColorLight(
            coordinator,
            hass,
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

    def __init__(self, coordinator, hass) -> None:
        super().__init__(coordinator)
        self.hass = hass

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }


class KarotzColorLight(
    KarotzBaseLight,
):
    device_id = "karotz_leds"
    device_name = "OpenKarotz LEDs"

    _attr_color_mode = ColorMode.RGB

    _attr_supported_color_modes = {ColorMode.RGB}

    def __init__(
        self,
        coordinator,
        hass,
        suffix,
        translation_key,
    ) -> None:
        super().__init__(coordinator, hass)

        self.suffix = suffix
        self.api = coordinator.api

        self.entity_id = f"light.openkarotz_color_{suffix}"

        self._attr_translation_key = translation_key

        self._attr_unique_id = f"openkarotz_color_{suffix}"

        self._attr_rgb_color = (
            0,
            255,
            0,
        )

        self._attr_is_on = True

    async def async_turn_on(
        self,
        **kwargs,
    ) -> None:

        rgb_color = kwargs.get("rgb_color")

        if rgb_color is not None:
            self._attr_rgb_color = rgb_color

        self._attr_is_on = True

        self.async_write_ha_state()

        # Apply LED settings immediately
        await apply_led_settings(self.hass, self.api)

    async def async_turn_off(
        self,
        **kwargs,
    ) -> None:

        self._attr_is_on = False

        self.async_write_ha_state()

        # Apply LED settings immediately
        await apply_led_settings(self.hass, self.api)
