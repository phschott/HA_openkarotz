from homeassistant.components.light import LightEntity

class KarotzLight(LightEntity):
    def __init__(self, api):
        self.api = api
        self._attr_name = "Karotz LED"

    async def async_turn_on(self, **kwargs):
        color = kwargs.get("rgb_color", (0,255,0))
        hex_color = "%02X%02X%02X" % color
        await self.api._get(f"/cgi-bin/leds?color={hex_color}")

    async def async_turn_off(self, **kwargs):
        await self.api._get("/cgi-bin/leds?color=000000")