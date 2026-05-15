import logging

import aiohttp
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"

VOICE_ENTITY = "select.openkarotz_voice"
TEXT_ENTITY = "text.openkarotz_tts"

MOOD_ENTITY = "select.openkarotz_mood"

LEFT_EAR_ENTITY = "number.openkarotz_ear_left"
RIGHT_EAR_ENTITY = "number.openkarotz_ear_right"

LED_1_ENTITY = "light.openkarotz_color_1"
LED_2_ENTITY = "light.openkarotz_color_2"

LED_SPEED_ENTITY = "number.openkarotz_pulse_speed"
LED_PULSE_ENTITY = "switch.openkarotz_led_pulse"


BUTTONS = [
    (
        "reboot",
        "mdi:restore",
        "karotz",
        "OpenKarotz",
        EntityCategory.CONFIG,
    ),
    (
        "wakeup",
        "mdi:weather-sunset-up",
        "karotz",
        "OpenKarotz",
        None,
    ),
    (
        "sleep",
        "mdi:power-sleep",
        "karotz",
        "OpenKarotz",
        None,
    ),
    (
        "ears_random",
        "mdi:rabbit-variant-outline",
        "karotz_ears",
        "OpenKarotz Ears",
        None,
    ),
    (
        "ears_reset",
        "mdi:restore",
        "karotz_ears",
        "OpenKarotz Ears",
        EntityCategory.CONFIG,
    ),
    (
        "led_off",
        "mdi:lightbulb-off",
        "karotz_leds",
        "OpenKarotz LEDs",
        None,
    ),
    (
        "random_mood",
        "mdi:emoticon-outline",
        "karotz_sound",
        "OpenKarotz Sound",
        None,
    ),
    (
        "clock",
        "mdi:clock",
        "karotz_sound",
        "OpenKarotz Sound",
        None,
    ),
    (
        "snapshot",
        "mdi:camera",
        "karotz_picture",
        "OpenKarotz Picture",
        None,
    ),
    (
        "clear_snapshots",
        "mdi:trash-can",
        "karotz_picture",
        "OpenKarotz Picture",
        EntityCategory.CONFIG,
    ),
]


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        KarotzButton(
            coordinator,
            method,
            icon,
            device_id,
            device_name,
            entity_category,
        )
        for (
            method,
            icon,
            device_id,
            device_name,
            entity_category,
        ) in BUTTONS
    ]

    entities.extend(
        [
            KarotzSpeakButton(coordinator),
            KarotzMoodButton(coordinator),
            KarotzMoveEarsButton(coordinator),
            KarotzApplyLedsButton(coordinator),
        ]
    )

    async_add_entities(entities)


class KarotzBaseButton(
    CoordinatorEntity,
    ButtonEntity,
):
    _attr_has_entity_name = True
    device_id: str
    device_name: str

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self.api = coordinator.api
        self.hass = coordinator.hass

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

    def _get_state(self, entity_id):
        return self.hass.states.get(entity_id)

    def _get_int_state(
        self,
        entity_id,
        default=0,
    ):
        state = self._get_state(entity_id)

        if state is None:
            return default

        try:
            return int(float(state.state))

        except (ValueError, TypeError):
            return default

    @staticmethod
    def _light_to_hex(state) -> str:

        if state is None or state.state == "off":
            return "000000"

        rgb = state.attributes.get(
            "rgb_color",
            (0, 0, 0),
        )

        return "%02X%02X%02X" % rgb


class KarotzButton(
    KarotzBaseButton,
):

    def __init__(
        self,
        coordinator,
        method,
        icon,
        device_id,
        device_name,
        entity_category=None,
    ):
        super().__init__(coordinator)

        self.method = method

        self.device_id = device_id
        self.device_name = device_name

        self._attr_translation_key = method
        self._attr_unique_id = (
            f"openkarotz_{method}"
        )
        self._attr_icon = icon
        self._attr_entity_category = (
            entity_category
        )

    async def async_press(self):
        try:
            await getattr(
                self.api,
                self.method,
            )()
        except aiohttp.ClientResponseError as err:
            # L'API a bien exécuté l'action malgré le header invalide
            _LOGGER.debug("Snapshot pris malgré header invalide (réponse DBus OpenKarotz): %s", err)
            return

class KarotzSpeakButton(
    KarotzBaseButton,
):

    device_id = "karotz_sound"
    device_name = "OpenKarotz Sound"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_translation_key = "speak"

        self._attr_unique_id = (
            "openkarotz_speak"
        )

        self._attr_icon = (
            "mdi:account-voice"
        )

    async def async_press(self):

        voice = self._get_state(
            VOICE_ENTITY
        )

        text = self._get_state(
            TEXT_ENTITY
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


class KarotzMoodButton(
    KarotzBaseButton,
):

    device_id = "karotz_sound"
    device_name = "OpenKarotz Sound"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_translation_key = "mood"

        self._attr_unique_id = (
            "openkarotz_mood"
        )

        self._attr_icon = (
            "mdi:emoticon-outline"
        )

    async def async_press(self):

        mood = self._get_state(
            MOOD_ENTITY
        )

        if mood is None:
            return

        mood_id = (
            mood.state.split("-")[0].strip()
        )

        await self.api.moods(
            mood_id,
        )


class KarotzMoveEarsButton(
    KarotzBaseButton,
):

    device_id = "karotz_ears"
    device_name = "OpenKarotz Ears"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_translation_key = "move_ears"

        self._attr_unique_id = (
            "openkarotz_move_ears"
        )

        self._attr_icon = (
            "mdi:rabbit"
        )

    async def async_press(self):

        left = self._get_int_state(
            LEFT_EAR_ENTITY
        )

        right = self._get_int_state(
            RIGHT_EAR_ENTITY
        )

        await self.api.ears(
            left,
            right,
        )


class KarotzApplyLedsButton(
    KarotzBaseButton,
):

    device_id = "karotz_leds"
    device_name = "OpenKarotz LEDs"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_translation_key = "apply_leds"

        self._attr_unique_id = (
            "openkarotz_apply_leds"
        )

        self._attr_icon = (
            "mdi:lightbulb-on"
        )

    async def async_press(self):

        color1 = self._get_state(
            LED_1_ENTITY
        )

        color2 = self._get_state(
            LED_2_ENTITY
        )

        speed = self._get_int_state(
            LED_SPEED_ENTITY,
            0,
        )

        pulse = self._get_state(
            LED_PULSE_ENTITY
        )

        pulse_value = (
            0
            if pulse
            and pulse.state == "off"
            else 1
        )

        hex1 = self._light_to_hex(
            color1
        )

        hex2 = self._light_to_hex(
            color2
        )

        await self.api.leds(
            pulse_value,
            hex1,
            speed,
            hex2,
        )
