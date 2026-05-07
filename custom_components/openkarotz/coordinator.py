from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

class KarotzCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="karotz",
            update_interval=timedelta(minutes=5),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            return {
                "status": await self.api.get_status(),
                #"voices": await self.api.get_voices(),
                #"moods": await self.api.get_moods(),
                "snapshots": await self.api.get_snapshots(),
            }
        
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        