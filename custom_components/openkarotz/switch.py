from homeassistant.components.switch import (
    SwitchEntity,
)
from homeassistant.helpers.restore_state import (
    RestoreEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"


SWITCHES = [
    (
        "led_pulse",
        "karotz_leds",
        "OpenKarotz LEDs",
        "mdi:pulse",
        True,
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
        KarotzSwitch(
            coordinator,
            translation_key,
            device_id,
            device_name,
            icon,
            default_state,
        )
        for (
            translation_key,
            device_id,
            device_name,
            icon,
            default_state,
        ) in SWITCHES
    ]

    async_add_entities(entities)


class KarotzBaseSwitch(
    CoordinatorEntity,
    RestoreEntity,
    SwitchEntity,
):
    _attr_has_entity_name = True

    device_id: str
    device_name: str

    def __init__(
        self,
        coordinator,
    ):
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

    async def async_added_to_hass(
        self,
    ):
        await super().async_added_to_hass()

        last_state = (
            await self.async_get_last_state()
        )

        if last_state is not None:
            self._attr_is_on = (
                last_state.state == "on"
            )

    @property
    def is_on(self):
        return self._attr_is_on

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


class KarotzSwitch(
    KarotzBaseSwitch,
):

    def __init__(
        self,
        coordinator,
        translation_key,
        device_id,
        device_name,
        icon,
        default_state,
    ):
        super().__init__(coordinator)

        self.device_id = device_id
        self.device_name = device_name

        self._attr_translation_key = (
            translation_key
        )

        self._attr_unique_id = (
            f"openkarotz_{translation_key}"
        )

        self._attr_icon = icon

        self._attr_is_on = (
            default_state
        )