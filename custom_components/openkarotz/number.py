from homeassistant.components.number import (
    NumberEntity,
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


NUMBERS = [
    (
        "ear_left",
        "karotz_ears",
        "OpenKarotz Ears",
        "mdi:rabbit",
        0,
        16,
        1,
        8,
        "slider",
    ),
    (
        "ear_right",
        "karotz_ears",
        "OpenKarotz Ears",
        "mdi:rabbit",
        0,
        16,
        1,
        8,
        "slider",
    ),
    (
        "pulse_speed",
        "karotz_leds",
        "OpenKarotz LEDs",
        "mdi:speedometer",
        0,
        2000,
        1,
        700,
        "slider",
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
        KarotzNumber(
            coordinator,
            translation_key,
            device_id,
            device_name,
            icon,
            min_value,
            max_value,
            step,
            default_value,
            mode,
        )
        for (
            translation_key,
            device_id,
            device_name,
            icon,
            min_value,
            max_value,
            step,
            default_value,
            mode,
        ) in NUMBERS
    ]

    async_add_entities(entities)


class KarotzBaseNumber(
    CoordinatorEntity,
    RestoreEntity,
    NumberEntity,
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

    async def async_added_to_hass(
        self,
    ):
        await super().async_added_to_hass()

        last_state = (
            await self.async_get_last_state()
        )

        if last_state is None:
            return

        try:
            self._attr_native_value = (
                float(last_state.state)
            )

        except (
            ValueError,
            TypeError,
        ):
            pass

    async def async_set_native_value(
        self,
        value,
    ):
        self._attr_native_value = value

        self.async_write_ha_state()


class KarotzNumber(
    KarotzBaseNumber,
):

    def __init__(
        self,
        coordinator,
        translation_key,
        device_id,
        device_name,
        icon,
        min_value,
        max_value,
        step,
        default_value,
        mode,
    ):
        super().__init__(coordinator)

        self.device_id = device_id
        self.device_name = device_name

        self.entity_id = (
            f"number.openkarotz_{translation_key}"
        )

        self._attr_translation_key = (
            translation_key
        )

        self._attr_unique_id = (
            f"openkarotz_{translation_key}"
        )

        self._attr_icon = icon

        self._attr_native_min_value = (
            min_value
        )

        self._attr_native_max_value = (
            max_value
        )

        self._attr_native_step = step

        self._attr_native_value = (
            default_value
        )

        self._attr_mode = mode
