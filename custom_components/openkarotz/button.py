from homeassistant.components.button import ButtonEntity

from .const import DOMAIN

BUTTONS = [
    ("reboot", "Karotz Reboot"),
    ("wakeup", "Karotz Wake Up"),
    ("sleep", "Karotz Sleep"),
    ("ears_random", "Karotz Random Ears"),
    ("ears_reset", "Karotz Reset Ears"),
    ("snapshot", "Karotz Snapshot"),
    ("clear_snapshots", "Karotz Clear Snapshots"),
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
        KarotzButton(coordinator, method, name)
        for method, name in BUTTONS
    ]

    async_add_entities(entities)
    #async_add_entities(
    #    [
    #        KarotzRebootButton(coordinator),
    #        KarotzEarsRandomButton(coordinator),
    #    ]
    #)

class KarotzButton(ButtonEntity):

    def __init__(self, coordinator, method, name):
        self.coordinator = coordinator
        self.api = coordinator.api

        self.method = method

        self._attr_name = name
        self._attr_unique_id = f"openkarotz_{method}"

    async def async_press(self):
        await getattr(self.api, self.method)()