"""Light entities for OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
)

from .const import DEVICE_LEDS, DOMAIN
from .entity import KarotzEntity
from .led_helper import apply_led_settings

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from .shared_state import KarotzSharedState

HEX_COLOR_LENGTH = 6


LIGHTS = [
    {
        "suffix": "1",
        "translation_key": "color_1",
        "default_rgb": (0, 255, 0),  # Green
        "default_is_on": True,
    },
    {
        "suffix": "2",
        "translation_key": "color_2",
        "default_rgb": (0, 0, 0),  # Black (off)
        "default_is_on": False,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz light entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["fast_coordinator"]
    shared_state = hass.data[DOMAIN][entry.entry_id]["shared_state"]

    entities = [
        KarotzColorLight(
            coordinator,
            hass,
            shared_state,
            light_config,
        )
        for light_config in LIGHTS
    ]

    async_add_entities(entities)


class KarotzBaseLight(
    KarotzEntity,
    LightEntity,
):
    """Base class for OpenKarotz light entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        hass: HomeAssistant,
        shared_state: KarotzSharedState,
    ) -> None:
        """Initialize light entity."""
        super().__init__(coordinator)
        self.hass = hass
        self.shared_state = shared_state


class KarotzColorLight(
    KarotzBaseLight,
):
    """OpenKarotz color light entity."""

    device_id = DEVICE_LEDS

    _attr_color_mode = ColorMode.RGB

    _attr_supported_color_modes: ClassVar[set[ColorMode]] = {ColorMode.RGB}

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        hass: HomeAssistant,
        shared_state: KarotzSharedState,
        light_config: dict[str, Any],
    ) -> None:
        """Initialize light entity."""
        super().__init__(coordinator, hass, shared_state)

        self.suffix = light_config["suffix"]
        self.api = coordinator.api

        self._attr_translation_key = light_config["translation_key"]

        self._set_ids(f"color_{self.suffix}", "light")

        # Set default RGB color from configuration
        self._attr_rgb_color = light_config["default_rgb"]

        # Set default on/off state from configuration
        self._attr_is_on = light_config["default_is_on"]

        # Seed the shared state with this light's defaults.
        self._store_shared_state()

    def _store_shared_state(self) -> None:
        """Mirror this light's color/on state into the shared state."""
        setattr(self.shared_state, f"color_{self.suffix}_rgb", self._attr_rgb_color)
        setattr(self.shared_state, f"color_{self.suffix}_on", self._attr_is_on)

    def _handle_coordinator_update(self) -> None:
        """Sync LED color from device status (color_1 only)."""
        if self.suffix == "1" and self.coordinator.data:
            status = self.coordinator.data.get("status") or {}
            led_color = status.get("led_color")
            if led_color and len(led_color) == HEX_COLOR_LENGTH:
                try:
                    r = int(led_color[0:2], 16)
                    g = int(led_color[2:4], 16)
                    b = int(led_color[4:6], 16)
                    self._attr_rgb_color = (r, g, b)
                    self._attr_is_on = led_color != "000000"
                    self._store_shared_state()
                except ValueError:
                    pass
        super()._handle_coordinator_update()

    async def async_turn_on(
        self,
        **kwargs: Any,
    ) -> None:
        """Turn on light."""
        rgb_color = kwargs.get("rgb_color")

        if rgb_color is not None:
            self._attr_rgb_color = rgb_color

        self._attr_is_on = True

        self._store_shared_state()

        self.async_write_ha_state()

        # Apply LED settings immediately
        await apply_led_settings(self.api, self.shared_state)

    async def async_turn_off(
        self,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Turn off light."""
        self._attr_is_on = False

        self._store_shared_state()

        self.async_write_ha_state()

        # Apply LED settings immediately
        await apply_led_settings(self.api, self.shared_state)
