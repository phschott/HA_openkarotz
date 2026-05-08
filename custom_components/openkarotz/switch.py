from homeassistant.components.switch import (
    SwitchEntity,
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
            KarotzPulseSwitch(
                coordinator
            )
        ]
    )

class KarotzPulseSwitch(
    RestoreEntity,
    SwitchEntity,
):

    def __init__(self, coordinator):

        self.coordinator = coordinator

        self._attr_name = (
            "Karotz LED Pulse"
        )

        self._attr_unique_id = (
            "openkarotz_led_pulse"
        )

        self._attr_icon = (
            "mdi:pulse"
        )

        self._attr_is_on = True

    async def async_added_to_hass(
        self,
    ):
        await super().async_added_to_hass()

        last_state = (
            await self.async_get_last_state()
        )

        if last_state:
            self._attr_is_on = (
                last_state.state == "on"
            )

    async def async_turn_on(
        self,
        **kwargs,
    ):
        self._attr_is_on = True

        self.async_write_ha_state()

    async def async_turn_off(
        self,
        **kwargs,
    ):
        self._attr_is_on = False

        self.async_write_ha_state()

    @property
    def is_on(self):
        return self._attr_is_on

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
