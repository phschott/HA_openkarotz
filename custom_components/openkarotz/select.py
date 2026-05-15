import html

from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant.helpers.restore_state import (
    RestoreEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN

MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"


SELECTS = [
    (
        "voice",
        "voices",
        "voices",
        "lang",
        "mdi:account-voice",
    ),
    (
        "mood",
        "moods",
        "moods",
        "text",
        "mdi:emoticon-happy",
    ),
    (
        "radios",
        "streams",
        "streams",
        "name",
        "mdi:radio",
    ),
]


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Setup OpenKarotz select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    fast_coordinator = hass.data[DOMAIN][entry.entry_id][
        "fast_coordinator"
    ]

    entities = [
        KarotzSelect(
            coordinator,
            translation_key,
            data_key,
            options_key,
            option_label,
            icon,
        )
        for (
            translation_key,
            data_key,
            options_key,
            option_label,
            icon,
        ) in SELECTS
    ]

    entities.append(
        OpenKarotzSnapshotSelect(
            fast_coordinator,
        )
    )

    async_add_entities(entities)


class KarotzBaseSelect(
    CoordinatorEntity,
    RestoreEntity,
    SelectEntity,
):
    """Base class for OpenKarotz selects."""

    _attr_has_entity_name = True

    device_id = "karotz_sound"
    device_name = "OpenKarotz Sound"

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self.api = coordinator.api

        self._attr_options = []

        self._attr_current_option = None

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {
                (DOMAIN, self.device_id)
            },
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    async def async_added_to_hass(
        self,
    ):
        """Restore previous state."""
        await super().async_added_to_hass()

        last_state = (
            await self.async_get_last_state()
        )

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
    def available(self):
        """Return availability."""
        return (
            self.coordinator.last_update_success
        )


class KarotzSelect(
    KarotzBaseSelect,
):
    """Generic OpenKarotz select."""

    def __init__(
        self,
        coordinator,
        translation_key,
        data_key,
        options_key,
        option_label,
        icon,
    ):
        super().__init__(coordinator)

        self.data_key = data_key

        self.options_key = options_key

        self.option_label = option_label

        self.entity_id = (
            f"select.openkarotz_{translation_key}"
        )

        self._attr_translation_key = (
            translation_key
        )

        self._attr_unique_id = (
            f"openkarotz_{translation_key}"
        )

        self._attr_icon = icon

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

            item_id = item.get(
                "id",
                "unknown",
            )

            label = item.get(
                self.option_label,
                "Unknown",
            )

            label = html.unescape(label)

            options.append(
                f"{item_id} - {label}"
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

class OpenKarotzSnapshotSelect(
    KarotzBaseSelect,
):
    device_id = "karotz_picture"
    device_name = "OpenKarotz Picture"

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self.entity_id = (
            "select.openkarotz_snapshots"
        )

        self._attr_translation_key = (
            "snapshots"
        )

        self._attr_unique_id = (
            "openkarotz_snapshots"
        )

        self._attr_icon = "mdi:camera"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {
                (DOMAIN, self.device_id)
            },
            "name": self.device_name,
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }

    @property
    def options(self):

        options = [
            snap["id"]
            for snap in self.coordinator.data
                .get("snapshots", {})
                .get("snapshots", [])
            if "id" in snap
        ]

        self._attr_options = options

        return options

    @property
    def current_option(self):

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
        self._attr_current_option = option

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):

        if not self._attr_current_option:
            return {}

        filename = self._attr_current_option.replace(
            "snapshot_",
            "",
        )

        return {
            "snapshot_url":
                f"http://{self.api.host}"
                #f"http://karotz.schott.io:8080"
                f"/cgi-bin/snapshot_get"
                f"?filename=snapshot_{filename}"
        }
