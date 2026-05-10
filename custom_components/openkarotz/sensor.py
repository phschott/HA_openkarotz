from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

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
    hass,
    entry,
    async_add_entities,
):
    """Setup OpenKarotz sensors."""

    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    fast_coordinator = hass.data[DOMAIN][entry.entry_id][
        "fast_coordinator"
    ]

    entities = [
        KarotzStatusSensor(
            coordinator,
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

    entities.append(
        KarotzSnapshotCountSensor(
            fast_coordinator
        )
    )

    async_add_entities(entities)


class KarotzBaseSensor(
    CoordinatorEntity,
    SensorEntity,
):
    _attr_has_entity_name = True

    device_id: str
    device_name: str

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.device_id)
            },
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }


class KarotzStatusSensor(
    KarotzBaseSensor,
):

    device_id = "karotz"
    device_name = "OpenKarotz"

    def __init__(
        self,
        coordinator,
        key,
        unit,
        entity_category,
        state_class,
    ):
        super().__init__(coordinator)

        self.key = key

        self._attr_translation_key = key

        self._attr_unique_id = (
            f"openkarotz_{key}"
        )

        self._attr_native_unit_of_measurement = (
            unit
        )

        self._attr_entity_category = (
            entity_category
        )

        self._attr_state_class = (
            state_class
        )

    @property
    def native_value(self):

        status = self.coordinator.data.get(
            "status",
            {},
        )

        return status.get(self.key)


class KarotzSnapshotCountSensor(
    KarotzBaseSensor,
):

    device_id = "karotz_picture"
    device_name = "OpenKarotz Picture"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_translation_key = (
            "snapshots"
        )

        self._attr_unique_id = (
            "openkarotz_snapshots"
        )

        self._attr_state_class = (
            SensorStateClass.MEASUREMENT
        )

    @property
    def native_value(self):

        snapshots = (
            self.coordinator.data.get(
                "snapshots",
                {},
            ).get(
                "snapshots",
                [],
            )
        )

        return len(snapshots)