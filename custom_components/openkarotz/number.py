"""Number entities for OpenKarotz integration."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEVICE_EARS,
    DEVICE_LEDS,
    EAR_DEFAULT_VALUE,
    EAR_MAX_VALUE,
    EAR_MIN_VALUE,
    ENTITY_EAR_LEFT,
    ENTITY_EAR_RIGHT,
    LED_SPEED_DEFAULT_VALUE,
    LED_SPEED_MAX_VALUE,
    LED_SPEED_MIN_VALUE,
    MANUFACTURER,
    MODEL,
)

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


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        KarotzNumber(
            coordinator,
            number_config,
        )
        for number_config in NUMBERS
    ]

    async_add_entities(entities)


class KarotzBaseNumber(CoordinatorEntity, RestoreEntity, NumberEntity):
    """Base class for OpenKarotz number entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        """Initialize number entity."""
        super().__init__(coordinator)
        self.api = coordinator.api

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    async def async_added_to_hass(self):
        """Restore previous state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is None:
            return

        try:
            self._attr_native_value = float(last_state.state)
        except (ValueError, TypeError):
            pass

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self._attr_native_value = value
        self.async_write_ha_state()

        # Call device-specific handlers for ear movement
        await self._on_value_changed(value)

    async def _on_value_changed(self, value: float) -> None:
        """Handle value change - override in subclasses."""


class KarotzNumber(KarotzBaseNumber):
    """OpenKarotz number entity."""

    def __init__(self, coordinator, number_config):
        """Initialize number entity."""
        super().__init__(coordinator)

        self.device_id = number_config["device_id"]
        self.device_name = number_config["device_name"]
        self._attr_translation_key = number_config["translation_key"]
        self._attr_unique_id = f"openkarotz_{number_config['translation_key']}"
        self._attr_icon = number_config["icon"]
        self._attr_native_min_value = number_config["min_value"]
        self._attr_native_max_value = number_config["max_value"]
        self._attr_native_step = number_config["step"]
        self._attr_native_value = number_config["default_value"]
        self._attr_mode = number_config["mode"]
        self._attr_entity_category = number_config["entity_category"]

    async def _on_value_changed(self, value: float) -> None:
        """Handle ear movement on value change."""
        # Move ears when ear_left or ear_right changes
        if self.device_id == DEVICE_EARS:
            await self._move_ears_on_change()

    async def _move_ears_on_change(self) -> None:
        """Move ears when their values change."""
        try:
            left_state = self.hass.states.get(ENTITY_EAR_LEFT)
            right_state = self.hass.states.get(ENTITY_EAR_RIGHT)

            if left_state and right_state:
                left = int(float(left_state.state))
                right = int(float(right_state.state))
                await self.api.ears(left, right)
                _LOGGER.debug("Ears moved to left=%s, right=%s", left, right)
        except Exception as err:
            _LOGGER.warning("Failed to move ears: %s", err)
