import aiohttp

class KarotzAPI:
    def __init__(self, host):
        self.host = host

    async def _get(self, path):
        url = f"http://{self.host}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json(content_type=None)

    async def get_status(self):
        return await self._get("/cgi-bin/status")

    async def get_voices(self):
        return await self._get("/cgi-bin/voice_list")

    async def get_moods(self):
        return await self._get("/cgi-bin/moods_list")
    
    async def get_snapshots(self):
        return await self._get("/cgi-bin/snapshot_list")

    async def tts(self, voice, text):
        url = f"http://{self.host}/cgi-bin/tts?voice={voice}&text={text}"
        async with aiohttp.ClientSession() as session:
            await session.get(url)