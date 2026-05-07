from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    async_add_entities([
        KarotzVoiceSelect(coordinator)
    ])

class KarotzVoiceSelect(
    CoordinatorEntity,
    SelectEntity,
):

    def __init__(self, coordinator):
        super().__init__(coordinator)

        self.api = coordinator.api

        self._attr_name = "Karotz Voice"

        self._attr_unique_id = (
            "openkarotz_voice"
        )

        self._attr_icon = "mdi:account-voice"

        self._current_option = None

    @property
    def options(self):

        voices_data = self.coordinator.data[
            "voices"
        ]

        voices = voices_data.get(
            "voices",
            []
        )

        return [
            f"{v['id']} - {v['lang']}"
            for v in voices
        ]
    
        @property
        def current_option(self):
            return self._current_option
        
    async def async_select_option(self, option, ):
        self._current_option = option

        self.async_write_ha_state()