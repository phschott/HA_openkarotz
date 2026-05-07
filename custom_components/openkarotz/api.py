import aiohttp

class KarotzAPI:
    def __init__(self, host):
        self.host = host
            
    async def _get(self, path):
        url = f"http://{self.host}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json(content_type=None)

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

    async def ears_reset(self):
        await self._get("/cgi-bin/ears_reset")

    async def led_off(self):
        await self._get("/cgi-bin/leds?color=000000")

    # =====================
    # VOICE / TTS
    # =====================

    async def moods(self):
        await self._get("/cgi-bin/apps/moods")

    async def clock(self):
        await self._get("/cgi-bin/apps/clock")
    
    async def tts(self, voice, text):
        await self._get("/cgi-bin/tts?voice={voice}&text={text}")

    # =====================
    # SNAPSHOT / WEBCAM
    # =====================

    async def snapshot(self):
        await self._get("/cgi-bin/snapshot?silent=1")

    async def clear_snapshots(self):
        await self._get("/cgi-bin/clear_snapshots")

    async def get_snapshots(self):
        return await self._get("/cgi-bin/snapshot_list")