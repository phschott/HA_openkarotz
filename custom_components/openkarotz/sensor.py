from homeassistant.helpers.entity import Entity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities([KarotzVersionSensor(coordinator)])


class KarotzVersionSensor(Entity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Karotz Version"

    @property
    def state(self):
        return self.coordinator.data.get("version")

    async def async_update(self):
        await self.coordinator.async_request_refresh()