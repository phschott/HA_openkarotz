from homeassistant.components.button import ButtonEntity

from .const import DOMAIN

BUTTONS = [
    ("reboot", "Karotz Reboot", "mdi:restore"),
    ("wakeup", "Karotz Wake Up", "mdi:weather-sunset-up"),
    ("sleep", "Karotz Sleep", "mdi:power-sleep"),
    ("ears_random", "Karotz Random Ears", "mdi:rabbit-variant-outline"),
    ("ears_reset", "Karotz Reset Ears", "mdi:restore"),
    ("snapshot", "Karotz Snapshot", "mdi:camera"),
    ("clear_snapshots", "Karotz Clear Snapshots", "mdi:trash-can"),
]

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities = [
        KarotzButton(coordinator, method, name, icon)
        for method, name, icon in BUTTONS
    ]

    async_add_entities(entities)
    #async_add_entities(
    #    [
    #        KarotzRebootButton(coordinator),
    #        KarotzEarsRandomButton(coordinator),
    #    ]
    #)

class KarotzButton(ButtonEntity):

    def __init__(self, coordinator, method, name, icon):
        self.coordinator = coordinator
        self.api = coordinator.api

        self.method = method

        self._attr_name = name
        self._attr_unique_id = f"openkarotz_{method}"
        self._attr_icon = icon

    async def async_press(self):
        await getattr(self.api, self.method)()