import html

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Setup OpenKarotz select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    async_add_entities(
        [
            KarotzVoiceSelect(coordinator),
            KarotzMoodSelect(coordinator),
            KarotzRadioSelect(coordinator),
        ]
    )


class KarotzBaseSelect(
    CoordinatorEntity,
    RestoreEntity,
    SelectEntity,
):
    """Base class for OpenKarotz selects."""

    data_key = None
    options_key = None
    option_label = None

    def __init__(
        self,
        coordinator,
        name,
        unique_id,
        icon,
    ):
        """Initialize select."""
        super().__init__(coordinator)

        self.api = coordinator.api

        self._attr_name = name

        self._attr_unique_id = unique_id

        self._attr_icon = icon

        self._attr_options = []

        self._attr_current_option = None

    async def async_added_to_hass(self):
        """Restore previous state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if (
            last_state
            and last_state.state
            in self.options
        ):
            self._attr_current_option = (
                last_state.state
            )

        elif self.options:
            self._attr_current_option = (
                self.options[0]
            )

    @property
    def options(self):
        """Return available options."""
        data = self.coordinator.data.get(
            self.data_key,
            {},
        )

        values = data.get(
            self.options_key,
            [],
        )

        options = []

        for item in values:

            label = item.get(
                self.option_label,
                "Unknown",
            )

            label = html.unescape(label)

            options.append(
                f"{item['id']} - {label}"
            )

        self._attr_options = options

        return options

    @property
    def current_option(self):
        """Return selected option."""
        if (
            self._attr_current_option
            not in self.options
        ):
            if self.options:
                self._attr_current_option = (
                    self.options[0]
                )

        return self._attr_current_option

    async def async_select_option(
        self,
        option,
    ):
        """Handle selection."""
        if option not in self.options:
            return

        self._attr_current_option = option

        self.async_write_ha_state()

    @property
    def available(self):
        """Return availability."""
        return (
            self.coordinator.last_update_success
        )

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {
                ("openkarotz", "karotz_sound")
            },
            "name": "OpenKarotz Sound",
            "manufacturer": "Karotz",
            "model": "OpenKarotz",
        }


class KarotzVoiceSelect(
    KarotzBaseSelect,
):
    """Voice selector."""

    data_key = "voices"

    options_key = "voices"

    option_label = "lang"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "Karotz Voice",
            "openkarotz_voice",
            "mdi:account-voice",
        )


class KarotzMoodSelect(
    KarotzBaseSelect,
):
    """Mood selector."""

    data_key = "moods"

    options_key = "moods"

    option_label = "text"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "Karotz Mood",
            "openkarotz_mood",
            "mdi:emoticon-happy",
        )

class KarotzRadioSelect(
    KarotzBaseSelect,
):
    """Radio selector."""

    data_key = "streams"

    options_key = "streams"

    option_label = "name"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator,
            "Karotz radios",
            "openkarotz_radios",
            "mdi:radio",
        )
