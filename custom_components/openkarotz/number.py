from homeassistant.components.number import (
    NumberEntity,
)
from homeassistant.helpers.restore_state import (
    RestoreEntity,
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
            KarotzEarNumber(
                coordinator,
                "left",
                "Karotz Ear Left",
                "openkarotz_ear_left",
            ),
            KarotzEarNumber(
                coordinator,
                "right",
                "Karotz Ear Right",
                "openkarotz_ear_right",
            ),
            KarotzPulseSpeedNumber(
                coordinator,
                "pulse",
                "Karotz Pulse Speed",
                "karotz_pulse_speed",
            ),
        ]
    )

class KarotzEarNumber(
    RestoreEntity,
    NumberEntity,
):

    def __init__(
        self,
        coordinator,
        side,
        name,
        unique_id,
    ):
        self.coordinator = coordinator

        self.side = side

        self._attr_name = name

        self._attr_unique_id = unique_id

        self._attr_icon = (
            "mdi:rabbit"
        )

        self._attr_native_min_value = 0

        self._attr_native_max_value = 16

        self._attr_native_step = 1

        self._attr_native_value = 8

        self._attr_mode = "slider"

    async def async_added_to_hass(
        self,
    ):
        await super().async_added_to_hass()

        last_state = (
            await self.async_get_last_state()
        )

        if last_state:
            try:
                self._attr_native_value = (
                    float(last_state.state)
                )
            except Exception:
                pass

    async def async_set_native_value(
        self,
        value,
    ):
        self._attr_native_value = value

        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz_ears")
            },
            "name": "OpenKarotz Ears",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }

class KarotzPulseSpeedNumber(
    RestoreEntity,
    NumberEntity,
):

    def __init__(
        self,
        coordinator,
        side,
        name,
        unique_id,
    ):

        self.coordinator = coordinator

        self._attr_name = name

        self._attr_unique_id = unique_id

        self._attr_icon = (
            "mdi:speedometer"
        )

        self._attr_native_min_value = 0

        self._attr_native_max_value = 2000

        self._attr_native_step = 1

        self._attr_native_value = 700

    async def async_set_native_value(
        self,
        value,
    ):
        self._attr_native_value = value

        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz_leds")
            },
            "name": "OpenKarotz Leds",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }
