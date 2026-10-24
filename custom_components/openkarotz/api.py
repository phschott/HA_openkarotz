"""OpenKarotz API client."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)

# Keep requests short so an unreachable rabbit can't hold a poll for long.
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class KarotzAPI:
    """OpenKarotz API client for HTTP communication."""

    def __init__(self, host: str, session: ClientSession) -> None:
        """Initialize API client with device host and a shared HTTP session."""
        self.host = host
        # Home Assistant's shared client session; never closed by this client.
        self._session = session

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make GET request to API endpoint."""
        url = f"http://{self.host}{path}"
        try:
            async with self._session.get(
                url, params=params, timeout=REQUEST_TIMEOUT
            ) as resp:
                return await resp.json(content_type=None)
        except Exception as err:
            _LOGGER.warning("API request failed for %s: %s", path, err)
            raise

    async def _get_binary(
        self, path: str, params: dict[str, Any] | None = None
    ) -> bytes:
        """Get binary data from API endpoint."""
        url = f"http://{self.host}{path}"
        try:
            async with self._session.get(
                url, params=params, timeout=REQUEST_TIMEOUT
            ) as resp:
                return await resp.read()
        except Exception as err:
            _LOGGER.warning("Binary API request failed for %s: %s", path, err)
            raise

    # =====================
    # STATUS / POWER
    # =====================
    async def get_status(self) -> Any:
        """Get device status."""
        return await self._get("/cgi-bin/status")

    async def reboot(self) -> None:
        """Reboot the device."""
        await self._get("/cgi-bin/reboot")

    async def wakeup(self) -> None:
        """Wake up the device."""
        await self._get("/cgi-bin/wakeup", params={"silent": 1})

    async def sleep(self) -> None:
        """Put device to sleep."""
        await self._get("/cgi-bin/sleep")

    # =====================
    # GET LISTS for SELECTS
    # =====================
    async def get_voices(self) -> Any:
        """Get available voices list."""
        return await self._get("/cgi-bin/voice_list")

    async def get_moods(self) -> Any:
        """Get available moods list."""
        return await self._get("/cgi-bin/moods_list")

    async def get_radios(self) -> Any:
        """Get available radios list."""
        return await self._get("/cgi-bin/radios_list")

    # =====================
    # EARS / LEDS
    # =====================
    async def ears_random(self) -> None:
        """Move ears to random position."""
        await self._get("/cgi-bin/ears_random")

    async def ears(self, left: int, right: int) -> None:
        """
        Move ears to specific positions.

        Args:
            left: Left ear position (0-16)
            right: Right ear position (0-16)

        """
        await self._get(
            "/cgi-bin/ears",
            params={"left": left, "right": right, "noreset": 1},
        )

    async def ears_reset(self) -> None:
        """Reset ears to default position."""
        await self._get("/cgi-bin/ears_reset")

    async def led_off(self) -> None:
        """Turn off LEDs."""
        await self._get("/cgi-bin/leds", params={"color": "000000"})

    async def leds(
        self, pulse: int, hex_color1: str, speed: int, hex_color2: str
    ) -> None:
        """
        Control LED colors and animation.

        Args:
            pulse: Pulse mode (0 or 1)
            hex_color1: First color in hex format (RRGGBB)
            speed: Animation speed (0-2000)
            hex_color2: Second color in hex format (RRGGBB)

        """
        await self._get(
            "/cgi-bin/leds",
            params={
                "pulse": pulse,
                "color": hex_color1,
                "speed": speed,
                "color2": hex_color2,
            },
        )

    # =====================
    # VOICE / TTS / MOODS
    # =====================
    async def random_mood(self) -> None:
        """Play random mood animation."""
        await self._get("/cgi-bin/apps/moods")

    async def moods(self, mood_id: str) -> None:
        """Play specific mood animation."""
        await self._get("/cgi-bin/apps/moods", params={"id": mood_id})

    async def clock(self) -> None:
        """Display clock."""
        await self._get("/cgi-bin/apps/clock")

    async def tts(self, voice_id: str, text: str) -> None:
        """
        Play text-to-speech.

        Args:
            voice_id: Voice identifier
            text: Text to speak

        """
        await self._get("/cgi-bin/tts", params={"voice": voice_id, "text": text})

    # =====================
    # AUDIO / RADIOS
    # =====================
    async def get_sounds(self) -> Any:
        """Get list of available local sounds."""
        return await self._get("/cgi-bin/sound_list")

    async def play_sound(self, sound_id: str) -> None:
        """Play a local sound by id."""
        await self._get("/cgi-bin/sound", params={"id": sound_id})

    async def sound_url(self, karotz_stream_url: str) -> None:
        """Play audio from URL."""
        await self._get("/cgi-bin/sound", params={"url": karotz_stream_url})

    async def sound_pause(self) -> None:
        """Pause audio playback."""
        await self._get("/cgi-bin/sound_control", params={"cmd": "pause"})

    async def sound_quit(self) -> None:
        """Stop audio playback."""
        await self._get("/cgi-bin/sound_control", params={"cmd": "quit"})

    async def sound_control(self, cmd: str) -> None:
        """
        Control audio playback.

        Args:
            cmd: Control command (play, pause, stop, etc.)

        """
        await self._get("/cgi-bin/sound_control", params={"cmd": cmd})

    # =====================
    # SNAPSHOT / WEBCAM
    # =====================
    async def snapshot(self) -> None:
        """Take a snapshot."""
        await self._get("/cgi-bin/snapshot", params={"silent": 1})

    async def clear_snapshots(self) -> None:
        """Clear all snapshots."""
        await self._get("/cgi-bin/clear_snapshots")

    async def get_snapshots(self) -> Any:
        """Get list of available snapshots."""
        return await self._get("/cgi-bin/snapshot_list")

    async def snapshot_get(self, filename: str) -> bytes:
        """Get snapshot image by filename."""
        return await self._get_binary(
            "/cgi-bin/snapshot_get", params={"filename": filename}
        )
