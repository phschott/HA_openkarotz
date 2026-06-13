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
from .led_helper import apply_led_settings

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
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        KarotzSwitch(
            coordinator,
            hass,
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
        hass,
    ) -> None:
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

    async def async_added_to_hass(
        self,
    ) -> None:
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._attr_is_on = last_state.state == "on"

    @property
    def is_on(self):
        return self._attr_is_on

    async def async_turn_on(
        self,
        **kwargs,
    ) -> None:
        self._attr_is_on = True

        self.async_write_ha_state()

        # Apply LED settings immediately
        await self._on_state_changed()

    async def async_turn_off(
        self,
        **kwargs,
    ) -> None:
        self._attr_is_on = False

        self.async_write_ha_state()

        # Apply LED settings immediately
        await self._on_state_changed()

    async def _on_state_changed(self) -> None:
        """Handle state change - override in subclasses."""


class KarotzSwitch(
    KarotzBaseSwitch,
):
    def __init__(
        self,
        coordinator,
        hass,
        translation_key,
        device_id,
        device_name,
        icon,
        default_state,
    ) -> None:
        super().__init__(coordinator, hass)

        self.device_id = device_id
        self.device_name = device_name
        self.api = coordinator.api

        self.entity_id = f"switch.openkarotz_{translation_key}"

        self._attr_translation_key = translation_key

        self._attr_unique_id = f"openkarotz_{translation_key}"

        self._attr_icon = icon

        self._attr_is_on = default_state

    async def _on_state_changed(self) -> None:
        """Apply LED settings when pulse switch changes."""
        if self.device_id == "karotz_leds":
            await apply_led_settings(self.hass, self.api)
