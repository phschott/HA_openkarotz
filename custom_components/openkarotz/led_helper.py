"""LED helper utilities for OpenKarotz integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import KarotzAPI

from .const import (
    ENTITY_LED_COLOR_1,
    ENTITY_LED_COLOR_2,
    ENTITY_LED_PULSE,
    ENTITY_PULSE_SPEED,
)

_LOGGER = logging.getLogger(__name__)


def get_light_hex_color(hass: HomeAssistant, entity_id: str) -> str:
    """Convert light state to hex color."""
    state = hass.states.get(entity_id)

    if state is None or state.state == "off":
        return "000000"

    rgb = state.attributes.get("rgb_color", (0, 0, 0))
    return "{:02X}{:02X}{:02X}".format(*rgb)


def get_pulse_value(hass: HomeAssistant) -> int:
    """Get pulse mode from switch state."""
    pulse_state = hass.states.get(ENTITY_LED_PULSE)
    return 0 if pulse_state and pulse_state.state == "off" else 1


def get_pulse_speed(hass: HomeAssistant) -> int:
    """Get pulse speed from number entity."""
    speed_state = hass.states.get(ENTITY_PULSE_SPEED)
    if speed_state is None:
        return 0

    try:
        return int(float(speed_state.state))
    except ValueError, TypeError:
        return 0


async def apply_led_settings(hass: HomeAssistant, api: KarotzAPI) -> None:
    """Apply all LED settings to the device."""
    try:
        hex_color1 = get_light_hex_color(hass, ENTITY_LED_COLOR_1)
        hex_color2 = get_light_hex_color(hass, ENTITY_LED_COLOR_2)
        speed = get_pulse_speed(hass)
        pulse = get_pulse_value(hass)

        await api.leds(pulse, hex_color1, speed, hex_color2)

        _LOGGER.debug(
            "LEDs applied: pulse=%s, color1=%s, speed=%s, color2=%s",
            pulse,
            hex_color1,
            speed,
            hex_color2,
        )
    except Exception:
        _LOGGER.exception("Failed to apply LED settings")
