import aiohttp


class KarotzAPI:
    def __init__(self, host):
        self.host = host

    async def _get(self, path):
        url = f"http://{self.host}{path}"
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            return await resp.json(content_type=None)

    async def _get_binary(self, path):
        """Get binary data from API endpoint."""
        url = f"http://{self.host}{path}"
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            return await resp.read()

    # =====================
    # STATUS / POWER
    # =====================
    async def get_status(self):
        return await self._get("/cgi-bin/status")

    async def reboot(self):
        await self._get("/cgi-bin/reboot")

    async def wakeup(self):
        await self._get("/cgi-bin/wakeup?silent=1")

    async def sleep(self):
        await self._get("/cgi-bin/sleep")

    # =====================
    # GET LISTS for SELECTS
    # =====================

    async def get_voices(self):
        return await self._get("/cgi-bin/voice_list")

    async def get_moods(self):
        return await self._get("/cgi-bin/moods_list")

    # =====================
    # EARS / LEDS
    # =====================

    async def ears_random(self):
        await self._get("/cgi-bin/ears_random")

    async def ears(self, left, right):
        await self._get(f"/cgi-bin/ears?left={left}&right={right}&noreset=1")

    async def ears_reset(self):
        await self._get("/cgi-bin/ears_reset")

    async def led_off(self):
        await self._get("/cgi-bin/leds?color=000000")

    async def leds(self, pulse, hex1, speed, hex2):
        await self._get(f"/cgi-bin/leds?pulse={pulse}&color={hex1}&speed={speed}&color2={hex2}")

    # =====================
    # VOICE / TTS
    # =====================

    async def random_mood(self):
        await self._get("/cgi-bin/apps/moods")

    async def moods(self, mood):
        await self._get(f"/cgi-bin/apps/moods?id={mood}")

    async def clock(self):
        await self._get("/cgi-bin/apps/clock")

    async def tts(self, voice, text):
        await self._get(
            f"/cgi-bin/tts?voice={voice}&text={text}"
        )

    # =====================
    # RADIOS
    # =====================

    async def get_radios(self):
        await self._get("/cgi-bin/radios_list")

    async def sound_url(self, karotzStreamUrl):
        await self._get(f"/cgi-bin/sound?url={karotzStreamUrl}")

    async def sound_control(self, cmd):
        await self._get(f"/cgi-bin/sound_control?cmd={cmd}")

    # =====================
    # SNAPSHOT / WEBCAM
    # =====================

    async def snapshot(self):
        await self._get("/cgi-bin/snapshot?silent=1")

    async def clear_snapshots(self):
        await self._get("/cgi-bin/clear_snapshots")

    async def get_snapshots(self):
        return await self._get("/cgi-bin/snapshot_list")

    async def snapshot_get(self, filename):
        """Get snapshot image by filename."""
        return await self._get_binary(f"/cgi-bin/snapshot_get?filename={filename}")
