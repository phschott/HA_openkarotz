"""Image entity for OpenKarotz integration."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from homeassistant.components.image import ImageEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class KarotzSnapshotSlotImage(CoordinatorEntity, ImageEntity):
    """
    Image entity exposing the Nth most recent snapshot.

    One entity is created per gallery slot (slot 0 = most recent snapshot).
    Bound to a ``picture-entity`` card, tapping a slot opens Home Assistant's
    native full-screen image dialog. Content is read from the local cache
    populated by the fast coordinator, so it loads fast and works remotely.
    """

    _attr_has_entity_name = True
    _attr_content_type = "image/jpeg"

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        index: int,
    ) -> None:
        """Initialize a snapshot slot image entity."""
        super().__init__(coordinator)
        self.hass = hass
        self._index = index
        self.entity_id = f"image.openkarotz_snapshot_{index + 1}"
        self._attr_unique_id = f"openkarotz_snapshot_slot_{index + 1}"
        self._attr_name = f"Snapshot {index + 1}"
        self.device_id = "karotz_picture"
        self._current_id: str | None = None
        self._attr_image_last_updated = None
        # Minimal access-token support required by the image component.
        self._access_token = uuid.uuid4().hex
        self._access_tokens = [self._access_token]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information to group entities together."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": DEFAULT_NAME,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    def _snapshot_id(self) -> str | None:
        """Return the id of the snapshot for this slot, newest first."""
        data = self.coordinator.data or {}
        snaps = data.get("snapshots", {}).get("snapshots", [])
        ids = sorted(
            (s["id"] for s in snaps if isinstance(s, dict) and "id" in s),
            reverse=True,
        )
        if self._index < len(ids):
            return ids[self._index]
        return None

    @property
    def available(self) -> bool:
        """Slot is available only when a snapshot exists for its position."""
        return super().available and self._snapshot_id() is not None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Rotate the access token when this slot points to a new snapshot."""
        new_id = self._snapshot_id()
        if new_id != self._current_id:
            self._current_id = new_id
            self._access_token = uuid.uuid4().hex
            self._access_tokens = [self._access_token]
            self._attr_image_last_updated = dt_util.utcnow()
        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """Register coordinator listener and seed the current snapshot id."""
        await super().async_added_to_hass()
        self._current_id = self._snapshot_id()
        if self._current_id and self._attr_image_last_updated is None:
            self._attr_image_last_updated = dt_util.utcnow()

    async def async_image(self) -> bytes | None:
        """Return the cached bytes for this slot's snapshot."""
        snapshot_id = self._snapshot_id()
        if not snapshot_id:
            return None
        path = self.coordinator.snapshot_cache_dir / snapshot_id
        try:
            return await self.hass.async_add_executor_job(path.read_bytes)
        except FileNotFoundError:
            return None
        except Exception:
            _LOGGER.exception("Failed to read snapshot slot image %s", snapshot_id)
            return None

    @property
    def access_tokens(self) -> list[str]:
        """Return access tokens used by the image helper."""
        return self._access_tokens
