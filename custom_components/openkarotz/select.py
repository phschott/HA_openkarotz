from homeassistant.components.select import SelectEntity
import html

class KarotzMoodSelect(SelectEntity):
    def __init__(self, api):
        self.api = api
        self._attr_name = "Karotz Mood"
        self._options = []

    async def async_update(self):
        data = await self.api.get_moods()
        moods = data.get("moods", [])
        self._options = [
            f"{m['id']} - {html.unescape(m['text'])}"
            for m in moods
        ]

    @property
    def options(self):
        return self._options

    async def async_select_option(self, option):
        mood_id = option.split("-")[0].strip()
        await self.api._get(f"/cgi-bin/apps/moods?id={mood_id}")