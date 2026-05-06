from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class KarotzCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            logger=None,
            name="karotz",
            update_interval=timedelta(minutes=5),
        )
        self.api = api

    async def _async_update_data(self):
        return await self.api.get_status()