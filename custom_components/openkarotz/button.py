from homeassistant.components.button import ButtonEntity

class KarotzRebootButton(ButtonEntity):
    def __init__(self, api):
        self.api = api
        self._attr_name = "Reboot Karotz"

    async def async_press(self):
        await self.api._get("/cgi-bin/reboot")