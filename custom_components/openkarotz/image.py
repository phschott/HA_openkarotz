import logging
from homeassistant.components.image import ImageEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Setup OpenKarotz image entities."""

    fast_coordinator = hass.data[DOMAIN][entry.entry_id]["fast_coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    entities = []

    # Get snapshots from fast_coordinator data
    snapshots = (
        fast_coordinator.data.get("snapshots", {})
        .get("snapshots", [])
    )

    _LOGGER.debug("Setting up image entities for %d snapshots", len(snapshots))

    # Create an image entity for each snapshot
    for snapshot in snapshots:
        entities.append(
            KarotzSnapshotImage(
                fast_coordinator,
                api,
                snapshot,
            )
        )

    async_add_entities(entities)


class KarotzSnapshotImage(CoordinatorEntity, ImageEntity):
    """Representation of a Karotz snapshot image."""

    _attr_has_entity_name = True
    device_id = "karotz_picture"
    device_name = "OpenKarotz Picture"

    def __init__(self, coordinator, api, snapshot):
        """Initialize the image entity."""
        super().__init__(coordinator)
        self._api = api
        self._snapshot = snapshot

        # Create safe name from filename
        safe_name = snapshot.replace("/", "_").replace(".jpg", "")
        self._attr_translation_key = "snapshot"
        self._attr_unique_id = f"openkarotz_snapshot_{safe_name}"
        self._attr_name = f"Snapshot {safe_name}"

        _LOGGER.debug("Created image entity for snapshot: %s", snapshot)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    async def async_image(self):
        """Return image data."""
        try:
            return await self._api.snapshot_get(self._snapshot)
        except Exception as err:
            _LOGGER.error(
                "Failed to get snapshot image %s: %s",
                self._snapshot,
                err,
            )
            return None
