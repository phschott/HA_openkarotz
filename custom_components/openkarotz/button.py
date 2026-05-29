"""Button entities for OpenKarotz integration."""
import logging

import aiohttp
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_EARS,
    DEVICE_KAROTZ,
    DEVICE_LEDS,
    DEVICE_PICTURE,
    DEVICE_SOUND,
    DOMAIN,
    ENTITY_LED_COLOR_1,
    ENTITY_LED_COLOR_2,
    ENTITY_LED_PULSE,
    ENTITY_MOOD_SELECT,
    ENTITY_PULSE_SPEED,
    ENTITY_TTS_TEXT,
    ENTITY_VOICE_SELECT,
    MANUFACTURER,
    MODEL,
)

_LOGGER = logging.getLogger(__name__)

BUTTONS = [
    {
        "method": "reboot",
        "icon": "mdi:restore",
        "device_id": DEVICE_KAROTZ,
        "device_name": "OpenKarotz",
        "entity_category": EntityCategory.CONFIG,
    },
    {
        "method": "wakeup",
        "icon": "mdi:weather-sunset-up",
        "device_id": DEVICE_KAROTZ,
        "device_name": "OpenKarotz",
        "entity_category": None,
    },
    {
        "method": "sleep",
        "icon": "mdi:power-sleep",
        "device_id": DEVICE_KAROTZ,
        "device_name": "OpenKarotz",
        "entity_category": None,
    },
    {
        "method": "ears_random",
        "icon": "mdi:rabbit-variant-outline",
        "device_id": DEVICE_EARS,
        "device_name": "OpenKarotz Ears",
        "entity_category": None,
    },
    {
        "method": "ears_reset",
        "icon": "mdi:restore",
        "device_id": DEVICE_EARS,
        "device_name": "OpenKarotz Ears",
        "entity_category": EntityCategory.CONFIG,
    },
    {
        "method": "led_off",
        "icon": "mdi:lightbulb-off",
        "device_id": DEVICE_LEDS,
        "device_name": "OpenKarotz LEDs",
        "entity_category": None,
    },
    {
        "method": "random_mood",
        "icon": "mdi:emoticon-outline",
        "device_id": DEVICE_SOUND,
        "device_name": "OpenKarotz Sound",
        "entity_category": None,
    },
    {
        "method": "clock",
        "icon": "mdi:clock",
        "device_id": DEVICE_SOUND,
        "device_name": "OpenKarotz Sound",
        "entity_category": None,
    },
    {
        "method": "snapshot",
        "icon": "mdi:camera",
        "device_id": DEVICE_PICTURE,
        "device_name": "OpenKarotz Picture",
        "entity_category": None,
    },
    {
        "method": "clear_snapshots",
        "icon": "mdi:trash-can",
        "device_id": DEVICE_PICTURE,
        "device_name": "OpenKarotz Picture",
        "entity_category": EntityCategory.CONFIG,
    },
]


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        KarotzButton(coordinator, button_config) for button_config in BUTTONS
    ]

    entities.extend(
        [
            KarotzSpeakButton(coordinator),
            KarotzMoodButton(coordinator),
            KarotzApplyLedsButton(coordinator),
        ]
    )

    async_add_entities(entities)


class KarotzBaseButton(CoordinatorEntity, ButtonEntity):
    """Base class for OpenKarotz button entities."""

    _attr_has_entity_name = True
    device_id: str
    device_name: str

    def __init__(self, coordinator) -> None:
        """Initialize button entity."""
        super().__init__(coordinator)
        self.api = coordinator.api
        self.hass = coordinator.hass

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _get_state(self, entity_id: str):
        """Get entity state."""
        return self.hass.states.get(entity_id)

    def _get_int_state(self, entity_id: str, default: int = 0) -> int:
        """Get entity state as integer."""
        state = self._get_state(entity_id)
        if state is None:
            return default

        try:
            return int(float(state.state))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _light_to_hex(state) -> str:
        """Convert light state to hex color."""
        if state is None or state.state == "off":
            return "000000"

        rgb = state.attributes.get("rgb_color", (0, 0, 0))
        return "{:02X}{:02X}{:02X}".format(*rgb)


class KarotzButton(KarotzBaseButton):
    """OpenKarotz button entity."""

    def __init__(self, coordinator, button_config) -> None:
        """Initialize button entity."""
        super().__init__(coordinator)

        self.method = button_config["method"]
        self.device_id = button_config["device_id"]
        self.device_name = button_config["device_name"]

        self._attr_translation_key = self.method
        self._attr_unique_id = f"openkarotz_{self.method}"
        self._attr_icon = button_config["icon"]
        self._attr_entity_category = button_config["entity_category"]

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            await getattr(self.api, self.method)()
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug(
                "API request completed despite header issue: %s", err
            )


class KarotzSpeakButton(KarotzBaseButton):
    """Button to speak TTS with selected voice."""

    device_id = DEVICE_SOUND
    device_name = "OpenKarotz Sound"

    def __init__(self, coordinator) -> None:
        """Initialize speak button."""
        super().__init__(coordinator)
        self._attr_translation_key = "speak"
        self._attr_unique_id = "openkarotz_speak"
        self._attr_icon = "mdi:account-voice"

    async def async_press(self) -> None:
        """Speak selected text with selected voice."""
        voice_state = self._get_state(ENTITY_VOICE_SELECT)
        text_state = self._get_state(ENTITY_TTS_TEXT)

        if not voice_state or not text_state:
            _LOGGER.warning(
                "Missing voice selection or text for TTS. Voice: %s, Text: %s",
                voice_state,
                text_state,
            )
            return

        if not text_state.state or text_state.state.strip() == "":
            _LOGGER.warning("TTS text is empty")
            return

        try:
            voice_id = voice_state.state.split("-")[0].strip()
            await self.api.tts(voice_id, text_state.state)
            _LOGGER.debug(
                "TTS speaking with voice %s: %s", voice_id, text_state.state
            )
        except Exception as err:
            _LOGGER.exception("Failed to speak TTS: %s", err)


class KarotzMoodButton(KarotzBaseButton):
    """Button to play selected mood."""

    device_id = DEVICE_SOUND
    device_name = "OpenKarotz Sound"

    def __init__(self, coordinator) -> None:
        """Initialize mood button."""
        super().__init__(coordinator)
        self._attr_translation_key = "mood"
        self._attr_unique_id = "openkarotz_mood"
        self._attr_icon = "mdi:emoticon-outline"

    async def async_press(self) -> None:
        """Play selected mood."""
        mood_state = self._get_state(ENTITY_MOOD_SELECT)

        if mood_state is None:
            _LOGGER.warning("No mood selected")
            return

        try:
            mood_id = mood_state.state.split("-")[0].strip()
            await self.api.moods(mood_id)
            _LOGGER.debug("Playing mood %s", mood_id)
        except Exception as err:
            _LOGGER.exception("Failed to play mood: %s", err)

class KarotzApplyLedsButton(KarotzBaseButton):
    """Button to apply LED color and animation settings."""

    device_id = DEVICE_LEDS
    device_name = "OpenKarotz LEDs"

    def __init__(self, coordinator) -> None:
        """Initialize apply LEDs button."""
        super().__init__(coordinator)
        self._attr_translation_key = "apply_leds"
        self._attr_unique_id = "openkarotz_apply_leds"
        self._attr_icon = "mdi:lightbulb-on"

    async def async_press(self) -> None:
        """Apply LED colors and animation settings."""
        color1_state = self._get_state(ENTITY_LED_COLOR_1)
        color2_state = self._get_state(ENTITY_LED_COLOR_2)
        speed = self._get_int_state(ENTITY_PULSE_SPEED, 0)
        pulse_state = self._get_state(ENTITY_LED_PULSE)

        # Determine pulse mode
        pulse_value = 0 if pulse_state and pulse_state.state == "off" else 1

        # Convert light states to hex colors
        hex_color1 = self._light_to_hex(color1_state)
        hex_color2 = self._light_to_hex(color2_state)

        try:
            await self.api.leds(pulse_value, hex_color1, speed, hex_color2)
            _LOGGER.debug(
                "LEDs applied: pulse=%s, color1=%s, speed=%s, color2=%s",
                pulse_value,
                hex_color1,
                speed,
                hex_color2,
            )
        except Exception as err:
            _LOGGER.exception("Failed to apply LED settings: %s", err)
