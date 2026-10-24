"""Sensor entities for OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"


SENSORS = [
    (
        "version",
        None,
        EntityCategory.DIAGNOSTIC,
        None,
    ),
    (
        "karotz_percent_used_space",
        "%",
        EntityCategory.DIAGNOSTIC,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "led_color",
        None,
        EntityCategory.DIAGNOSTIC,
        None,
    ),
    (
        "led_pulse",
        None,
        EntityCategory.DIAGNOSTIC,
        None,
    ),
    (
        "wlan_mac",
        None,
        EntityCategory.DIAGNOSTIC,
        None,
    ),
    (
        "nb_tags",
        None,
        None,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "nb_stories",
        None,
        None,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "nb_sounds",
        None,
        None,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "nb_moods",
        None,
        None,
        SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenKarotz sensors."""
    fast_coordinator = hass.data[DOMAIN][entry.entry_id]["fast_coordinator"]
    snapshot_coordinator = hass.data[DOMAIN][entry.entry_id]["snapshot_coordinator"]

    entities = [
        KarotzStatusSensor(
            fast_coordinator,
            key,
            unit,
            entity_category,
            state_class,
        )
        for (
            key,
            unit,
            entity_category,
            state_class,
        ) in SENSORS
    ]

    entities.append(KarotzSnapshotCountSensor(snapshot_coordinator))

    async_add_entities(entities)


class KarotzBaseSensor(
    CoordinatorEntity,
    SensorEntity,
):
    """Base class for OpenKarotz sensor entities."""

    _attr_has_entity_name = True

    device_id: str
    device_name: str

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize sensor entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }


class KarotzStatusSensor(
    KarotzBaseSensor,
):
    """OpenKarotz status sensor."""

    device_id = "karotz"
    device_name = "OpenKarotz"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        key: str,
        unit: str | None,
        entity_category: EntityCategory | None,
        state_class: SensorStateClass | None,
    ) -> None:
        """Initialize status sensor."""
        super().__init__(coordinator)

        self.key = key

        self._attr_translation_key = key

        self._attr_unique_id = f"openkarotz_{key}"

        self._attr_native_unit_of_measurement = unit

        self._attr_entity_category = entity_category

        self._attr_state_class = state_class

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        status = self.coordinator.data.get(
            "status",
            {},
        )

        return status.get(self.key)


class KarotzSnapshotCountSensor(
    KarotzBaseSensor,
):
    """Sensor counting the number of stored snapshots."""

    device_id = "karotz_picture"
    device_name = "OpenKarotz Picture"

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize snapshot count sensor."""
        super().__init__(coordinator)

        self._attr_translation_key = "snapshots"

        self._attr_unique_id = "openkarotz_snapshots"

        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the number of stored snapshots."""
        return len(self._snapshots())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """
        Expose the id of every stored snapshot.

        This lets a dashboard iterate over the snapshots; the images
        themselves are served through the authenticated image entities
        (``image.openkarotz_snapshot_N``), not as public ``/local/...`` URLs.
        """
        return {
            "snapshots": [
                {"id": snap["id"]} for snap in self._snapshots() if "id" in snap
            ]
        }

    def _snapshots(self) -> list[dict[str, Any]]:
        """Return the raw snapshot list from the coordinator data."""
        return self.coordinator.data.get(
            "snapshots",
            {},
        ).get(
            "snapshots",
            [],
        )
