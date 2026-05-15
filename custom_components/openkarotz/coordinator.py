import logging
from datetime import timedelta

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
            update_interval=timedelta(hours=4),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            return {
                "status": await self.api.get_status(),
                "voices": await self.api.get_voices(),
                "moods": await self.api.get_moods(),
                #"snapshots": await self.api.get_snapshots(),
                "radios": await self.api.get_radios(),
            }

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class MyFastCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="my_fast_data",
            update_interval=timedelta(seconds=10),
        )

        self.api = api

    async def _async_update_data(self):
        try:
            return {
                "snapshots": await self.api.get_snapshots(),
            }

        except Exception as err:
            raise UpdateFailed(f"Fast update failed: {err}") from err
