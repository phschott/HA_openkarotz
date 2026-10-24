"""Button entities for OpenKarotz integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_EARS,
    DEVICE_KAROTZ,
    DEVICE_LEDS,
    DEVICE_PICTURE,
    DEVICE_SOUND,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SNAPSHOT_REFRESH_DELAY,
)

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from .shared_state import KarotzSharedState

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
        "method": "sound_pause",
        "icon": "mdi:pause",
        "device_id": DEVICE_SOUND,
        "device_name": "OpenKarotz Sound",
        "entity_category": None,
    },
    {
        "method": "sound_quit",
        "icon": "mdi:stop",
        "device_id": DEVICE_SOUND,
        "device_name": "OpenKarotz Sound",
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
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    snapshot_coordinator = hass.data[DOMAIN][entry.entry_id]["snapshot_coordinator"]
    shared_state = hass.data[DOMAIN][entry.entry_id]["shared_state"]

    entities = [KarotzButton(coordinator, button_config) for button_config in BUTTONS]

    entities.extend(
        [
            KarotzSpeakButton(coordinator, shared_state),
            KarotzMoodButton(coordinator, shared_state),
            KarotzPlaySoundButton(coordinator, shared_state),
            KarotzPlayRadioButton(coordinator, shared_state),
            KarotzSnapshotButton(coordinator, snapshot_coordinator),
            KarotzClearSnapshotsButton(coordinator, snapshot_coordinator),
        ]
    )

    async_add_entities(entities)


class KarotzBaseButton(CoordinatorEntity, ButtonEntity):
    """Base class for OpenKarotz button entities."""

    _attr_has_entity_name = True
    device_id: str
    device_name: str

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize button entity."""
        super().__init__(coordinator)
        self.api = coordinator.api
        self.hass = coordinator.hass

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }


class KarotzButton(KarotzBaseButton):
    """OpenKarotz button entity."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, button_config: dict[str, Any]
    ) -> None:
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
            _LOGGER.debug("API request completed despite header issue: %s", err)


class KarotzSnapshotButton(KarotzBaseButton):
    """Take a photo, then refresh the snapshot gallery."""

    device_id = DEVICE_PICTURE
    device_name = "OpenKarotz Picture"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        snapshot_coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize snapshot button."""
        super().__init__(coordinator)
        self.snapshot_coordinator = snapshot_coordinator
        self._attr_translation_key = "snapshot"
        self._attr_unique_id = "openkarotz_snapshot"
        self._attr_icon = "mdi:camera"

    async def async_press(self) -> None:
        """Take a photo, then refresh the gallery once the file is stored."""
        try:
            await self.api.snapshot()
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug("snapshot completed despite header issue: %s", err)

        # The device needs a moment to store the new file before it appears in
        # the snapshot list, so refresh after a short delay.
        async_call_later(
            self.hass,
            SNAPSHOT_REFRESH_DELAY,
            self._delayed_refresh,
        )

    async def _delayed_refresh(self, _now: datetime) -> None:
        """Refresh the snapshot coordinator (scheduled after a snapshot)."""
        await self.snapshot_coordinator.async_request_refresh()


class KarotzClearSnapshotsButton(KarotzBaseButton):
    """Delete all snapshots on the device and in the local HA cache."""

    device_id = DEVICE_PICTURE
    device_name = "OpenKarotz Picture"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        snapshot_coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize clear snapshots button."""
        super().__init__(coordinator)
        self.snapshot_coordinator = snapshot_coordinator
        self._attr_translation_key = "clear_snapshots"
        self._attr_unique_id = "openkarotz_clear_snapshots"
        self._attr_icon = "mdi:trash-can"
        self._attr_entity_category = EntityCategory.CONFIG

    async def async_press(self) -> None:
        """Clear snapshots on the Karotz, then purge the local cache."""
        try:
            await self.api.clear_snapshots()
        except aiohttp.ClientResponseError as err:
            _LOGGER.debug("clear_snapshots completed despite header issue: %s", err)

        # Drop the in-memory copies so HA reflects the deletion at once.
        self.snapshot_coordinator.clear_image_cache()

        # Refresh so the snapshot sensor/gallery update immediately.
        await self.snapshot_coordinator.async_request_refresh()


class KarotzSpeakButton(KarotzBaseButton):
    """Button to speak TTS with selected voice."""

    device_id = DEVICE_SOUND
    device_name = "OpenKarotz Sound"

    def __init__(
        self, coordinator: DataUpdateCoordinator, shared_state: KarotzSharedState
    ) -> None:
        """Initialize speak button."""
        super().__init__(coordinator)
        self.shared_state = shared_state
        self._attr_translation_key = "speak"
        self._attr_unique_id = "openkarotz_speak"
        self._attr_icon = "mdi:account-voice"

    async def async_press(self) -> None:
        """Speak selected text with selected voice."""
        voice = self.shared_state.voice
        text = self.shared_state.tts_text

        if not voice:
            _LOGGER.warning("Missing voice selection for TTS")
            return

        if not text or text.strip() == "":
            _LOGGER.warning("TTS text is empty")
            return

        try:
            voice_id = voice.split("-")[0].strip()
            await self.api.tts(voice_id, text)
            _LOGGER.debug("TTS speaking with voice %s: %s", voice_id, text)
        except Exception:
            _LOGGER.exception("Failed to speak TTS")


class KarotzMoodButton(KarotzBaseButton):
    """Button to play selected mood."""

    device_id = DEVICE_SOUND
    device_name = "OpenKarotz Sound"

    def __init__(
        self, coordinator: DataUpdateCoordinator, shared_state: KarotzSharedState
    ) -> None:
        """Initialize mood button."""
        super().__init__(coordinator)
        self.shared_state = shared_state
        self._attr_translation_key = "mood"
        self._attr_unique_id = "openkarotz_mood"
        self._attr_icon = "mdi:emoticon-outline"

    async def async_press(self) -> None:
        """Play selected mood."""
        mood = self.shared_state.mood

        if not mood:
            _LOGGER.warning("No mood selected")
            return

        try:
            mood_id = mood.split("-")[0].strip()
            await self.api.moods(mood_id)
            _LOGGER.debug("Playing mood %s", mood_id)
        except Exception:
            _LOGGER.exception("Failed to play mood")


class KarotzPlaySoundButton(KarotzBaseButton):
    """Button to play the selected local sound."""

    device_id = DEVICE_SOUND
    device_name = "OpenKarotz Sound"

    def __init__(
        self, coordinator: DataUpdateCoordinator, shared_state: KarotzSharedState
    ) -> None:
        """Initialize play sound button."""
        super().__init__(coordinator)
        self.shared_state = shared_state
        self._attr_translation_key = "play_sound"
        self._attr_unique_id = "openkarotz_play_sound"
        self._attr_icon = "mdi:music-note"

    async def async_press(self) -> None:
        """Play the selected local sound."""
        sound = self.shared_state.sound

        if not sound:
            _LOGGER.warning("No sound selected")
            return

        try:
            sound_id = sound.strip()
            await self.api.play_sound(sound_id)
            _LOGGER.debug("Playing sound %s", sound_id)
        except Exception:
            _LOGGER.exception("Failed to play sound")


class KarotzPlayRadioButton(KarotzBaseButton):
    """Button to play the selected radio stream."""

    device_id = DEVICE_SOUND
    device_name = "OpenKarotz Sound"

    def __init__(
        self, coordinator: DataUpdateCoordinator, shared_state: KarotzSharedState
    ) -> None:
        """Initialize play radio button."""
        super().__init__(coordinator)
        self.shared_state = shared_state
        self._attr_translation_key = "play_radio"
        self._attr_unique_id = "openkarotz_play_radio"
        self._attr_icon = "mdi:radio"

    async def async_press(self) -> None:
        """Play the selected radio stream."""
        radio = self.shared_state.radio

        if not radio:
            _LOGGER.warning("No radio selected")
            return

        try:
            radio_id_str = radio.split(" - ")[0].strip()
            streams = (
                self.coordinator.data.get("radios", {}).get("streams", [])
                if self.coordinator.data
                else []
            )
            stream = next(
                (s for s in streams if str(s.get("id")) == radio_id_str),
                None,
            )

            if stream is None:
                _LOGGER.warning("Radio stream not found for id %s", radio_id_str)
                return

            await self.api.sound_url(stream["url"])
            _LOGGER.debug("Playing radio %s (%s)", stream.get("name"), stream["url"])
        except Exception:
            _LOGGER.exception("Failed to play radio")
