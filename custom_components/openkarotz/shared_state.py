"""Shared per-config-entry runtime state for OpenKarotz entities."""

from __future__ import annotations

from dataclasses import dataclass, field

from .const import EAR_DEFAULT_VALUE, LED_SPEED_DEFAULT_VALUE


@dataclass
class KarotzSharedState:
    """
    Mutable state shared between the OpenKarotz entities of one config entry.

    Entities write their current selection/value here and read each other's
    values from here, instead of looking entities up by entity_id through
    ``hass.states``. Entity ids are generated from the (translatable) device
    and entity names, so they differ between languages and break when a user
    renames an entity; a shared object sidesteps that entirely.
    """

    # Sound device: the raw option strings selected in the select entities
    # (e.g. "1 - EN"), parsed by the buttons exactly as before.
    voice: str | None = None
    tts_text: str = ""
    mood: str | None = None
    sound: str | None = None
    radio: str | None = None

    # Ear positions (0-16).
    ear_left: int = EAR_DEFAULT_VALUE
    ear_right: int = EAR_DEFAULT_VALUE

    # LED settings.
    pulse_speed: int = LED_SPEED_DEFAULT_VALUE
    led_pulse: bool = True
    color_1_rgb: tuple[int, int, int] = field(default=(0, 255, 0))
    color_1_on: bool = True
    color_2_rgb: tuple[int, int, int] = field(default=(0, 0, 0))
    color_2_on: bool = False
