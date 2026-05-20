"""Data coordinators for OpenKarotz integration."""
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    COORDINATOR_FAST_UPDATE_INTERVAL,
    COORDINATOR_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class KarotzCoordinator(DataUpdateCoordinator):
    """Main coordinator for OpenKarotz data updates (4-hour interval)."""

    def __init__(self, hass, api):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenKarotz",
            update_interval=timedelta(seconds=COORDINATOR_UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            return {
                "status": await self.api.get_status(),
                "voices": await self.api.get_voices(),
                "moods": await self.api.get_moods(),
                "radios": await self.api.get_radios(),
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class FastCoordinator(DataUpdateCoordinator):
    """Fast coordinator for frequently updated data (10-second interval)."""

    def __init__(self, hass, api):
        """Initialize the fast coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenKarotz Fast Data",
            update_interval=timedelta(seconds=COORDINATOR_FAST_UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch frequently updated data from API."""
        try:
            return {
                "snapshots": await self.api.get_snapshots(),
            }
        except Exception as err:
            raise UpdateFailed(f"Fast update failed: {err}") from err
