"""Number entities for OpenKarotz integration."""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_EARS,
    DEVICE_LEDS,
    DOMAIN,
    EAR_DEFAULT_VALUE,
    EAR_MAX_VALUE,
    EAR_MIN_VALUE,
    LED_SPEED_DEFAULT_VALUE,
    LED_SPEED_MAX_VALUE,
    LED_SPEED_MIN_VALUE,
    MANUFACTURER,
    MODEL,
)
from .led_helper import apply_led_settings

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from .shared_state import KarotzSharedState

_LOGGER = logging.getLogger(__name__)

NUMBERS = [
    {
        "translation_key": "ear_left",
        "device_id": DEVICE_EARS,
        "device_name": "OpenKarotz Ears",
        "icon": "mdi:rabbit",
        "min_value": EAR_MIN_VALUE,
        "max_value": EAR_MAX_VALUE,
        "step": 1,
        "default_value": EAR_DEFAULT_VALUE,
        "mode": "slider",
        "entity_category": None,
    },
    {
        "translation_key": "ear_right",
        "device_id": DEVICE_EARS,
        "device_name": "OpenKarotz Ears",
        "icon": "mdi:rabbit",
        "min_value": EAR_MIN_VALUE,
        "max_value": EAR_MAX_VALUE,
        "step": 1,
        "default_value": EAR_DEFAULT_VALUE,
        "mode": "slider",
        "entity_category": None,
    },
    {
        "translation_key": "pulse_speed",
        "device_id": DEVICE_LEDS,
        "device_name": "OpenKarotz LEDs",
        "icon": "mdi:speedometer",
        "min_value": LED_SPEED_MIN_VALUE,
        "max_value": LED_SPEED_MAX_VALUE,
        "step": 1,
        "default_value": LED_SPEED_DEFAULT_VALUE,
        "mode": "slider",
        "entity_category": None,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    shared_state = hass.data[DOMAIN][entry.entry_id]["shared_state"]

    entities = [
        KarotzNumber(
            coordinator,
            hass,
            shared_state,
            number_config,
        )
        for number_config in NUMBERS
    ]

    async_add_entities(entities)


class KarotzBaseNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """Base class for OpenKarotz number entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        hass: HomeAssistant,
        shared_state: KarotzSharedState,
    ) -> None:
        """Initialize number entity."""
        super().__init__(coordinator)
        self.api = coordinator.api
        self.hass = hass
        self.shared_state = shared_state

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    async def async_added_to_hass(self) -> None:
        """Restore previous state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            with contextlib.suppress(ValueError, TypeError):
                self._attr_native_value = float(last_state.state)

        # Seed the shared state with the current (restored or default) value so
        # the other entities read a consistent value before any user change.
        self._store_shared_value(self._attr_native_value)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._attr_native_value = value
        self._store_shared_value(value)
        self.async_write_ha_state()

        # Call device-specific handlers for ear movement or LED settings
        await self._on_value_changed(value)

    def _store_shared_value(self, value: float) -> None:
        """Write this entity's value into the shared state - override."""

    async def _on_value_changed(self, value: float) -> None:
        """Handle value change - override in subclasses."""


class KarotzNumber(KarotzBaseNumber):
    """OpenKarotz number entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        hass: HomeAssistant,
        shared_state: KarotzSharedState,
        number_config: dict[str, Any],
    ) -> None:
        """Initialize number entity."""
        super().__init__(coordinator, hass, shared_state)

        self.device_id = number_config["device_id"]
        self.device_name = number_config["device_name"]
        # Pin a stable, language-independent entity_id for the dashboard.
        self.entity_id = f"number.openkarotz_{number_config['translation_key']}"
        # Shared-state attribute this number maps to (ear_left/ear_right/
        # pulse_speed); matches the translation key.
        self._field = number_config["translation_key"]
        self._attr_translation_key = number_config["translation_key"]
        self._attr_unique_id = f"openkarotz_{number_config['translation_key']}"
        self._attr_icon = number_config["icon"]
        self._attr_native_min_value = number_config["min_value"]
        self._attr_native_max_value = number_config["max_value"]
        self._attr_native_step = number_config["step"]
        self._attr_native_value = number_config["default_value"]
        self._attr_mode = number_config["mode"]
        self._attr_entity_category = number_config["entity_category"]

    def _store_shared_value(self, value: float) -> None:
        """Store the value into the shared state."""
        setattr(self.shared_state, self._field, int(value))

    async def _on_value_changed(self, value: float) -> None:  # noqa: ARG002
        """Handle value change - move ears or apply LED settings."""
        if self.device_id == DEVICE_EARS:
            await self._move_ears_on_change()
        elif self.device_id == DEVICE_LEDS:
            # Apply LED settings immediately when pulse speed changes
            await apply_led_settings(self.api, self.shared_state)

    async def _move_ears_on_change(self) -> None:
        """Move both ears to the positions held in the shared state."""
        try:
            left = self.shared_state.ear_left
            right = self.shared_state.ear_right
            await self.api.ears(left, right)
            _LOGGER.debug("Ears moved to left=%s, right=%s", left, right)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Failed to move ears: %s", err)
