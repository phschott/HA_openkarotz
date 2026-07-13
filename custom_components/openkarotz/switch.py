"""Switch entities for OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["fast_coordinator"]

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
    """Base class for OpenKarotz switch entities."""

    _attr_has_entity_name = True

    device_id: str
    device_name: str

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        hass: HomeAssistant,
    ) -> None:
        """Initialize switch entity."""
        super().__init__(coordinator)
        self.hass = hass

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    async def async_added_to_hass(
        self,
    ) -> None:
        """Restore previous state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._attr_is_on = last_state.state == "on"

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        return self._attr_is_on

    async def async_turn_on(
        self,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Turn the switch on."""
        self._attr_is_on = True

        self.async_write_ha_state()

        # Apply LED settings immediately
        await self._on_state_changed()

    async def async_turn_off(
        self,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Turn the switch off."""
        self._attr_is_on = False

        self.async_write_ha_state()

        # Apply LED settings immediately
        await self._on_state_changed()

    async def _on_state_changed(self) -> None:
        """Handle state change - override in subclasses."""


class KarotzSwitch(
    KarotzBaseSwitch,
):
    """OpenKarotz switch entity."""

    def __init__(  # noqa: PLR0913
        self,
        coordinator: DataUpdateCoordinator,
        hass: HomeAssistant,
        translation_key: str,
        device_id: str,
        device_name: str,
        icon: str,
        default_state: bool,  # noqa: FBT001
    ) -> None:
        """Initialize switch entity."""
        super().__init__(coordinator, hass)

        self.device_id = device_id
        self.device_name = device_name
        self.api = coordinator.api

        self.entity_id = f"switch.openkarotz_{translation_key}"

        self._attr_translation_key = translation_key

        self._attr_unique_id = f"openkarotz_{translation_key}"

        self._attr_icon = icon

        self._attr_is_on = default_state

    def _handle_coordinator_update(self) -> None:
        """Sync LED pulse state from device status."""
        if self.device_id == "karotz_leds" and self.coordinator.data:
            status = self.coordinator.data.get("status") or {}
            led_pulse = status.get("led_pulse")
            if led_pulse is not None:
                self._attr_is_on = led_pulse == "1"
        super()._handle_coordinator_update()

    async def _on_state_changed(self) -> None:
        """Apply LED settings when pulse switch changes."""
        if self.device_id == "karotz_leds":
            await apply_led_settings(self.hass, self.api)
