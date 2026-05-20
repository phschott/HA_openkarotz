"""OpenKarotz API client."""
import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)


class KarotzAPI:
    """OpenKarotz API client for HTTP communication."""

    def __init__(self, host):
        """Initialize API client with device host."""
        self.host = host

    async def _get(self, path: str):
        """Make GET request to API endpoint."""
        url = f"http://{self.host}{path}"
        try:
            async with aiohttp.ClientSession() as session, session.get(url) as resp:
                return await resp.json(content_type=None)
        except Exception as err:
            _LOGGER.warning("API request failed for %s: %s", path, err)
            raise

    async def _get_binary(self, path: str):
        """Get binary data from API endpoint."""
        url = f"http://{self.host}{path}"
        try:
            async with aiohttp.ClientSession() as session, session.get(url) as resp:
                return await resp.read()
        except Exception as err:
            _LOGGER.warning("Binary API request failed for %s: %s", path, err)
            raise

    # =====================
    # STATUS / POWER
    # =====================
    async def get_status(self):
        """Get device status."""
        return await self._get("/cgi-bin/status")

    async def reboot(self):
        """Reboot the device."""
        await self._get("/cgi-bin/reboot")

    async def wakeup(self):
        """Wake up the device."""
        await self._get("/cgi-bin/wakeup?silent=1")

    async def sleep(self):
        """Put device to sleep."""
        await self._get("/cgi-bin/sleep")

    # =====================
    # GET LISTS for SELECTS
    # =====================
    async def get_voices(self):
        """Get available voices list."""
        return await self._get("/cgi-bin/voice_list")

    async def get_moods(self):
        """Get available moods list."""
        return await self._get("/cgi-bin/moods_list")

    async def get_radios(self):
        """Get available radios list."""
        return await self._get("/cgi-bin/radios_list")

    # =====================
    # EARS / LEDS
    # =====================
    async def ears_random(self):
        """Move ears to random position."""
        await self._get("/cgi-bin/ears_random")

    async def ears(self, left: int, right: int):
        """Move ears to specific positions.

        Args:
            left: Left ear position (0-16)
            right: Right ear position (0-16)
        """
        await self._get(f"/cgi-bin/ears?left={left}&right={right}&noreset=1")

    async def ears_reset(self):
        """Reset ears to default position."""
        await self._get("/cgi-bin/ears_reset")

    async def led_off(self):
        """Turn off LEDs."""
        await self._get("/cgi-bin/leds?color=000000")

    async def leds(self, pulse: int, hex_color1: str, speed: int, hex_color2: str):
        """Control LED colors and animation.

        Args:
            pulse: Pulse mode (0 or 1)
            hex_color1: First color in hex format (RRGGBB)
            speed: Animation speed (0-2000)
            hex_color2: Second color in hex format (RRGGBB)
        """
        await self._get(
            f"/cgi-bin/leds?pulse={pulse}&color={hex_color1}&speed={speed}&color2={hex_color2}"
        )

    # =====================
    # VOICE / TTS / MOODS
    # =====================
    async def random_mood(self):
        """Play random mood animation."""
        await self._get("/cgi-bin/apps/moods")

    async def moods(self, mood_id: str):
        """Play specific mood animation."""
        await self._get(f"/cgi-bin/apps/moods?id={mood_id}")

    async def clock(self):
        """Display clock."""
        await self._get("/cgi-bin/apps/clock")

    async def tts(self, voice_id: str, text: str):
        """Play text-to-speech.

        Args:
            voice_id: Voice identifier
            text: Text to speak
        """
        await self._get(f"/cgi-bin/tts?voice={voice_id}&text={text}")

    # =====================
    # AUDIO / RADIOS
    # =====================
    async def sound_url(self, karotz_stream_url: str):
        """Play audio from URL."""
        await self._get(f"/cgi-bin/sound?url={karotz_stream_url}")

    async def sound_control(self, cmd: str):
        """Control audio playback.

        Args:
            cmd: Control command (play, pause, stop, etc.)
        """
        await self._get(f"/cgi-bin/sound_control?cmd={cmd}")

    # =====================
    # SNAPSHOT / WEBCAM
    # =====================
    async def snapshot(self):
        """Take a snapshot."""
        await self._get("/cgi-bin/snapshot?silent=1")

    async def clear_snapshots(self):
        """Clear all snapshots."""
        await self._get("/cgi-bin/clear_snapshots")

    async def get_snapshots(self):
        """Get list of available snapshots."""
        return await self._get("/cgi-bin/snapshot_list")

    async def snapshot_get(self, filename: str):
        """Get snapshot image by filename."""
        return await self._get_binary(f"/cgi-bin/snapshot_get?filename={filename}")
