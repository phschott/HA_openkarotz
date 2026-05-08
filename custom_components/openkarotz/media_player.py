from homeassistant.components.media_player import MediaPlayerEntity


class KarotzMediaPlayer(MediaPlayerEntity):
    def __init__(self, api):
        self.api = api

    async def async_play_media(self, media_type, media_id, **kwargs):
        await self.api._get(f"/cgi-bin/sound?url={media_id}")

    async def async_media_pause(self):
        await self.api._get("/cgi-bin/sound_control?cmd=pause")

    async def async_media_stop(self):
        await self.api._get("/cgi-bin/sound_control?cmd=quit")
