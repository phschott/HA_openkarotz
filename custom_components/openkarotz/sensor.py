from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


SENSORS = [
    ("version", "Karotz Version", None),
    ("karotz_percent_used_space", "Karotz Used Space", "%"),
    ("led_color", "Karotz Led Color Raw", None),
    ("led_pulse", "Karotz Led Pulse Raw", None),
    ("wlan_mac", "Karotz WLAN MAC", None),
    ("nb_tags", "Karotz Nb Tags", None),
    ("nb_stories", "Karotz Nb Stories", None),
    ("nb_sounds", "Karotz Nb Sounds", None),
    ("nb_moods", "Karotz Nb Moods", None),
]

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup OpenKarotz sensors."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []

    for key, name, unit in SENSORS:
        entities.append(
            KarotzStatusSensor(
                coordinator,
                key,
                name,
                unit,
            )
        )

    # Exemple sensor snapshots
    entities.append(
        KarotzSnapshotCountSensor(coordinator)
    )

    async_add_entities(entities)

class KarotzStatusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)

        self.key = key

        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"openkarotz_{key}"

    @property
    def native_value(self):
        return self.coordinator.data["status"].get(self.key)
    
    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz")
            },
            "name": "OpenKarotz",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }

class KarotzSnapshotCountSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "Karotz Snapshots"
        self._attr_unique_id = "openkarotz_snapshots"

    @property
    def native_value(self):
        snapshots = self.coordinator.data["snapshots"].get(
            "snapshots", []
        )

        return len(snapshots)
    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz")
            },
            "name": "OpenKarotz",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }