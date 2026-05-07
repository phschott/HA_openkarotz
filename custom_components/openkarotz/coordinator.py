from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

import logging

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
        _LOGGER.debug("Fetching Karotz status")
        return await self.api.get_status()