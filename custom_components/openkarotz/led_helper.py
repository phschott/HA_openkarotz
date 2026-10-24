"""LED helper utilities for OpenKarotz integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import KarotzAPI
    from .shared_state import KarotzSharedState

_LOGGER = logging.getLogger(__name__)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an RGB tuple to the device's RRGGBB hex string."""
    return "{:02X}{:02X}{:02X}".format(*rgb)


async def apply_led_settings(api: KarotzAPI, state: KarotzSharedState) -> None:
    """Apply all LED settings to the device from the shared state."""
    try:
        hex_color1 = _rgb_to_hex(state.color_1_rgb) if state.color_1_on else "000000"
        hex_color2 = _rgb_to_hex(state.color_2_rgb) if state.color_2_on else "000000"
        speed = state.pulse_speed
        pulse = 1 if state.led_pulse else 0

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
