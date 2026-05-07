from homeassistant.components.button import ButtonEntity

from .const import DOMAIN

BUTTONS = [
    ("reboot", "Karotz Reboot", "mdi:restore"),
    ("wakeup", "Karotz Wake Up", "mdi:weather-sunset-up"),
    ("sleep", "Karotz Sleep", "mdi:power-sleep"),
    ("ears_random", "Karotz Random Ears", "mdi:rabbit-variant-outline"),
    ("ears_reset", "Karotz Reset Ears", "mdi:restore"),
    ("led_off", "Karotz Turn Off LEDs", "mdi:lightbulb-off"),
    ("moods", "Karotz Random Moods", "mdi:emoticon-outline"),
    ("clock", "Karotz Clock", "mdi:clock"),
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

    # Ajouter ici les boutons spécifiques
    entities.append(
        KarotzSpeakButton(coordinator)
    )

    async_add_entities(entities)

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

class KarotzSpeakButton(ButtonEntity):

    def __init__(self, coordinator):

        self.coordinator = coordinator

        self.api = coordinator.api

        self.hass = coordinator.hass

        self._attr_name = (
            "Karotz Speak"
        )

        self._attr_unique_id = (
            "openkarotz_speak"
        )

        self._attr_icon = (
            "mdi:account-voice"
        )

    async def async_press(self):

        voice_entity = (
            "select.karotz_voice"
        )

        text_entity = (
            "text.karotz_tts"
        )

        voice = self.hass.states.get(
            voice_entity
        )

        text = self.hass.states.get(
            text_entity
        )

        if not voice or not text:
            return

        voice_id = (
            voice.state.split("-")[0].strip()
        )

        await self.api.tts(
            voice_id,
            text.state,
        )

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