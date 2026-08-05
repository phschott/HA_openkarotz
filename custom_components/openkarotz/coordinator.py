"""Data coordinators for OpenKarotz integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    COORDINATOR_FAST_UPDATE_INTERVAL,
    COORDINATOR_UPDATE_INTERVAL,
    SNAPSHOT_CACHE_DIR,
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
    Coordinator for the snapshot list and local cache, refreshed on demand.

    It has no polling interval: the device snapshot list only changes when a
    photo is taken or the snapshots are cleared. Refreshing happens at
    integration load and when the picture buttons request it, instead of every
    few seconds.
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
        # Directory (under config/www) where snapshots are cached so Home
        # Assistant can serve them at /local/<SNAPSHOT_CACHE_DIR>/...
        self.snapshot_cache_dir = Path(hass.config.path(f"www/{SNAPSHOT_CACHE_DIR}"))

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the snapshot list and mirror it into the local cache."""
        try:
            snapshots = await self.api.get_snapshots()
        except Exception as err:
            msg = f"Snapshot update failed: {err}"
            raise UpdateFailed(msg) from err

        # Mirror the device snapshots into the local cache (best effort — a
        # failed download must not break the whole update cycle).
        try:
            await self._sync_snapshot_cache(snapshots)
        except Exception:
            _LOGGER.exception("Failed to sync snapshot cache")

        return {"snapshots": snapshots}

    @staticmethod
    def _thumb_name(snapshot_id: str) -> str:
        """Derive the thumbnail filename from a snapshot id."""
        return f"{snapshot_id.rsplit('.', 1)[0]}.thumb.gif"

    async def _sync_snapshot_cache(self, snapshots: Any) -> None:
        """Download new snapshots and drop ones removed from the device."""
        snaps = snapshots.get("snapshots", []) if isinstance(snapshots, dict) else []
        ids = [s["id"] for s in snaps if isinstance(s, dict) and "id" in s]

        wanted: set[str] = set()
        for snapshot_id in ids:
            wanted.add(snapshot_id)
            wanted.add(self._thumb_name(snapshot_id))

        existing = await self.hass.async_add_executor_job(self._ensure_and_list_cache)

        # Download the full image and thumbnail for any snapshot we lack.
        for filename in wanted - existing:
            try:
                content = await self.api.snapshot_get(filename)
            except Exception:  # noqa: BLE001
                _LOGGER.debug("Could not download snapshot file %s", filename)
                continue
            if content:
                await self.hass.async_add_executor_job(
                    self._write_file,
                    self.snapshot_cache_dir / filename,
                    content,
                )

        # Remove local files for snapshots that no longer exist on the device.
        for filename in existing - wanted:
            await self.hass.async_add_executor_job(
                self._remove_file,
                self.snapshot_cache_dir / filename,
            )

    async def async_clear_cache(self) -> None:
        """Delete every locally cached snapshot file."""
        await self.hass.async_add_executor_job(self._clear_cache)

    def _ensure_and_list_cache(self) -> set[str]:
        """Create the cache dir if needed and return the filenames it holds."""
        self.snapshot_cache_dir.mkdir(parents=True, exist_ok=True)
        return {p.name for p in self.snapshot_cache_dir.iterdir() if p.is_file()}

    def _clear_cache(self) -> None:
        """Remove all files from the cache directory."""
        if not self.snapshot_cache_dir.exists():
            return
        for path in self.snapshot_cache_dir.iterdir():
            if path.is_file():
                path.unlink(missing_ok=True)

    @staticmethod
    def _write_file(path: Path, content: bytes) -> None:
        """Write bytes to disk (runs in an executor thread)."""
        path.write_bytes(content)

    @staticmethod
    def _remove_file(path: Path) -> None:
        """Delete a file if it exists (runs in an executor thread)."""
        path.unlink(missing_ok=True)
