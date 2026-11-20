"""Text entities for OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.text import (
    TextEntity,
)
from homeassistant.helpers.restore_state import (
    RestoreEntity,
)

from .const import DEVICE_SOUND, DOMAIN
from .entity import KarotzEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from .shared_state import KarotzSharedState


TEXTS = [
    (
        "tts",
        DEVICE_SOUND,
        "mdi:text-box",
        "",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up text entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    shared_state = hass.data[DOMAIN][entry.entry_id]["shared_state"]

    entities = [
        KarotzText(
            coordinator,
            shared_state,
            translation_key,
            device_id,
            icon,
            default_value,
        )
        for (
            translation_key,
            device_id,
            icon,
            default_value,
        ) in TEXTS
    ]

    async_add_entities(entities)


class KarotzBaseText(
    KarotzEntity,
    RestoreEntity,
    TextEntity,
):
    """Base class for OpenKarotz text entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        shared_state: KarotzSharedState,
    ) -> None:
        """Initialize text entity."""
        super().__init__(coordinator)
        self.shared_state = shared_state

    async def async_added_to_hass(
        self,
    ) -> None:
        """Restore previous state."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None and last_state.state not in (
            None,
            "unknown",
            "unavailable",
        ):
            self._attr_native_value = last_state.state

        # Seed the shared state with the current (restored or default) text.
        self.shared_state.tts_text = self._attr_native_value or ""

    async def async_set_value(
        self,
        value: str,
    ) -> None:
        """Set new text value."""
        self._attr_native_value = value
        self.shared_state.tts_text = value

        self.async_write_ha_state()


class KarotzText(
    KarotzBaseText,
):
    """OpenKarotz text entity."""

    def __init__(  # noqa: PLR0913
        self,
        coordinator: DataUpdateCoordinator,
        shared_state: KarotzSharedState,
        translation_key: str,
        device_id: str,
        icon: str,
        default_value: str,
    ) -> None:
        """Initialize text entity."""
        super().__init__(coordinator, shared_state)

        self.device_id = device_id

        self._attr_translation_key = translation_key

        self._set_ids(translation_key, "text")

        self._attr_icon = icon

        self._attr_native_value = default_value
