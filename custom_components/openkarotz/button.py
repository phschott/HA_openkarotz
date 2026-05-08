from homeassistant.components.button import ButtonEntity

from .const import DOMAIN

BUTTONS = [
    ("reboot", "Karotz Reboot", "mdi:restore"),
    ("wakeup", "Karotz Wake Up", "mdi:weather-sunset-up"),
    ("sleep", "Karotz Sleep", "mdi:power-sleep"),
    ("ears_random", "Karotz Random Ears", "mdi:rabbit-variant-outline"),
    ("ears_reset", "Karotz Reset Ears", "mdi:restore"),
    ("led_off", "Karotz Turn Off LEDs", "mdi:lightbulb-off"),
    ("random_mood", "Karotz Random Moods", "mdi:emoticon-outline"),
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
    entities.append(
        KarotzMoodButton(coordinator)
    )

    entities.append(
        KarotzMoveEarsButton(coordinator)
    )

    entities.append(
        KarotzApplyLedsButton(coordinator)
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
            "text.openkarotz_karotz_tts"
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
                ("openkarotz", "karotz_tts")
            },
            "name": "OpenKarotz TTS",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }
class KarotzMoodButton(ButtonEntity):

    def __init__(self, coordinator):

        self.coordinator = coordinator

        self.api = coordinator.api

        self.hass = coordinator.hass

        self._attr_name = (
            "Karotz Mood"
        )

        self._attr_unique_id = (
            "openkarotz_mood"
        )

        self._attr_icon = (
            "mdi:emoticon-outline"
        )

    async def async_press(self):

        mood_entity = (
            "select.openkarotz_karotz_mood"
        )

        mood = self.hass.states.get(
            mood_entity
        )

        mood_id = (
            mood.state.split("-")[0].strip()
        )

        await self.api.moods(
            mood_id,
        )

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz_tts")
            },
            "name": "OpenKarotz TTS",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }

class KarotzMoveEarsButton(
    ButtonEntity,
):

    def __init__(self, coordinator):

        self.coordinator = coordinator

        self.api = coordinator.api

        self.hass = coordinator.hass

        self._attr_name = (
            "Karotz Move Ears"
        )

        self._attr_unique_id = (
            "openkarotz_move_ears"
        )

        self._attr_icon = (
            "mdi:rabbit"
        )

    async def async_press(self):

        left = self.hass.states.get(
            "number.openkarotz_karotz_ear_left"
        )

        right = self.hass.states.get(
            "number.openkarotz_karotz_ear_right"
        )

        if left is None or right is None:
            return

        await self.api.ears(
            int(float(left.state)),
            int(float(right.state)),
        )

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz_ears")
            },
            "name": "OpenKarotz Ears",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }

class KarotzApplyLedsButton(
    ButtonEntity,
):

    def __init__(self, coordinator):

        self.coordinator = coordinator

        self.api = coordinator.api

        self.hass = coordinator.hass

        self._attr_name = (
            "Karotz Apply LEDs"
        )

        self._attr_unique_id = (
            "openkarotz_apply_leds"
        )

        self._attr_icon = (
            "mdi:led-strip"
        )

    async def async_press(self):

        color1 = self.hass.states.get(
            "light.karotz_color_1"
        )

        color2 = self.hass.states.get(
            "light.karotz_color_2"
        )

        speed = self.hass.states.get(
            "number.karotz_pulse_speed"
        )

        pulse = self.hass.states.get(
            "switch.openkarotz_karotz_led_pulse"
        )

        pulse_value = 1

        if pulse and pulse.state == "off":
            pulse_value = 0

        if (
            color1 is None
            or color2 is None
            or speed is None
        ):
            return

        if color1.state == "off":
            hex1 = "000000"

        else:
            rgb1 = color1.attributes.get(
                "rgb_color",
                (0, 255, 0),
            )

            hex1 = "%02X%02X%02X" % rgb1

        if color2.state == "off":
            hex2 = "000000"

        else:
            rgb2 = color2.attributes.get(
                "rgb_color",
                (0, 0, 0),
            )

            hex2 = "%02X%02X%02X" % rgb2

        await self.api.leds(
            pulse_value,
            hex1,
            int(float(speed.state)),
            hex2,
        )

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("openkarotz", "karotz_leds")
            },
            "name": "OpenKarotz Leds",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }
