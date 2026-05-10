from homeassistant.components.text import (
    TextEntity,
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


TEXTS = [
    (
        "tts",
        "karotz_sound",
        "OpenKarotz Sound",
        "mdi:text-box",
        "",
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
        KarotzText(
            coordinator,
            translation_key,
            device_id,
            device_name,
            icon,
            default_value,
        )
        for (
            translation_key,
            device_id,
            device_name,
            icon,
            default_value,
        ) in TEXTS
    ]

    async_add_entities(entities)


class KarotzBaseText(
    CoordinatorEntity,
    RestoreEntity,
    TextEntity,
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

        if (
            last_state is not None
            and last_state.state
            not in (
                None,
                "unknown",
                "unavailable",
            )
        ):
            self._attr_native_value = (
                last_state.state
            )

    async def async_set_value(
        self,
        value,
    ):
        self._attr_native_value = value

        self.async_write_ha_state()


class KarotzText(
    KarotzBaseText,
):

    def __init__(
        self,
        coordinator,
        translation_key,
        device_id,
        device_name,
        icon,
        default_value,
    ):
        super().__init__(coordinator)

        self.device_id = device_id
        self.device_name = device_name
        self.entity_id = (
            f"text.openkarotz_{translation_key}"
        )

        self._attr_translation_key = (
            translation_key
        )

        self._attr_suggested_object_id = (
            translation_key
        )

        self._attr_unique_id = (
            f"openkarotz_{translation_key}"
        )

        self._attr_icon = icon

        self._attr_native_value = (
            default_value
        )