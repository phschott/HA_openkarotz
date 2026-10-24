"""Data coordinators for OpenKarotz integration."""

from __future__ import annotations

import logging
from collections import OrderedDict
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    COORDINATOR_FAST_UPDATE_INTERVAL,
    COORDINATOR_UPDATE_INTERVAL,
    SNAPSHOT_IMAGE_CACHE_SIZE,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import KarotzAPI

_LOGGER = logging.getLogger(__name__)


class KarotzCoordinator(DataUpdateCoordinator):
    """Main coordinator for OpenKarotz data updates (4-hour interval)."""

    def __init__(self, hass: HomeAssistant, api: KarotzAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenKarotz",
            update_interval=timedelta(seconds=COORDINATOR_UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            return {
                "voices": await self.api.get_voices(),
                "moods": await self.api.get_moods(),
                "radios": await self.api.get_radios(),
                "sounds": await self.api.get_sounds(),
            }
        except Exception as err:
            msg = f"Error communicating with API: {err}"
            raise UpdateFailed(msg) from err


class FastCoordinator(DataUpdateCoordinator):
    """Fast coordinator for frequently polled status (LED, diagnostic sensors)."""

    def __init__(self, hass: HomeAssistant, api: KarotzAPI) -> None:
        """Initialize the fast coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenKarotz Fast Data",
            update_interval=timedelta(seconds=COORDINATOR_FAST_UPDATE_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch frequently updated status from the device."""
        try:
            return {"status": await self.api.get_status()}
        except Exception as err:
            msg = f"Fast update failed: {err}"
            raise UpdateFailed(msg) from err


class SnapshotCoordinator(DataUpdateCoordinator):
    """
    Coordinator for the snapshot list, refreshed on demand.

    It has no polling interval: the device snapshot list only changes when a
    photo is taken or the snapshots are cleared. Refreshing happens at
    integration load and when the picture buttons request it, instead of every
    few seconds.

    Image bytes are never written under ``config/www`` (which would serve the
    rabbit's photos unauthenticated at ``/local/...``). They are fetched from
    the device on demand through Home Assistant's authenticated image proxy and
    kept in a small bounded in-memory cache.
    """

    def __init__(self, hass: HomeAssistant, api: KarotzAPI) -> None:
        """Initialize the snapshot coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenKarotz Snapshots",
            update_interval=None,
        )
        self.api = api
        # Most-recently-used cache of snapshot bytes, keyed by filename.
        self._image_cache: OrderedDict[str, bytes] = OrderedDict()

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the snapshot list from the device."""
        try:
            snapshots = await self.api.get_snapshots()
        except Exception as err:
            msg = f"Snapshot update failed: {err}"
            raise UpdateFailed(msg) from err

        # Drop cached bytes for snapshots that no longer exist on the device.
        self._prune_image_cache(snapshots)

        return {"snapshots": snapshots}

    async def async_get_image(self, filename: str) -> bytes | None:
        """
        Return the bytes of one snapshot, fetching from the device if needed.

        Results are cached in memory (bounded, MRU-evicted) so repeated reads
        of the same snapshot don't re-hit the device.
        """
        cached = self._image_cache.get(filename)
        if cached is not None:
            self._image_cache.move_to_end(filename)
            return cached

        content = await self.api.snapshot_get(filename)
        if not content:
            return None

        self._image_cache[filename] = content
        self._image_cache.move_to_end(filename)
        while len(self._image_cache) > SNAPSHOT_IMAGE_CACHE_SIZE:
            self._image_cache.popitem(last=False)
        return content

    def clear_image_cache(self) -> None:
        """Drop every cached snapshot (e.g. after clearing them on the device)."""
        self._image_cache.clear()

    def _prune_image_cache(self, snapshots: Any) -> None:
        """Evict cached bytes for snapshots removed from the device."""
        snaps = snapshots.get("snapshots", []) if isinstance(snapshots, dict) else []
        ids = {s["id"] for s in snaps if isinstance(s, dict) and "id" in s}
        for filename in [f for f in self._image_cache if f not in ids]:
            del self._image_cache[filename]
