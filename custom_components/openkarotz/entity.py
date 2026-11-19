"""Shared base entity for the OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import (
    CONF_NAME,
    DEFAULT_KAROTZ_NAME,
    DEVICE_KAROTZ,
    DEVICE_NAME_SUFFIXES,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


def karotz_name(entry: ConfigEntry) -> str:
    """Return the user-facing name of the Karotz behind a config entry."""
    return entry.data.get(CONF_NAME) or DEFAULT_KAROTZ_NAME


class KarotzEntity(CoordinatorEntity):
    """
    Base class for every OpenKarotz entity.

    All identities are scoped to the config entry, so several Karotz can be
    set up side by side:

    * ``unique_id``: ``<entry_id>_<key>``
    * device identifier: ``<entry_id>_<device_id>``
    * pinned ``entity_id``: ``<platform>.<slug of Karotz name>_<key>``; with the
      default name ``OpenKarotz`` this stays the historical
      ``<platform>.openkarotz_<key>`` used by ``dashboard.yaml``.
    """

    _attr_has_entity_name = True

    # One of the DEVICE_* constants; subclasses set it as class attribute or
    # in their __init__.
    device_id: str

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize the entity and bind it to the coordinator's entry."""
        super().__init__(coordinator)
        self.entry: ConfigEntry = coordinator.config_entry

    @property
    def karotz_name(self) -> str:
        """Return the user-facing name of this entity's Karotz."""
        return karotz_name(self.entry)

    def _set_ids(self, key: str, platform: str | None = None) -> None:
        """
        Set the per-entry unique_id and, if ``platform`` is given, pin entity_id.

        The entity_id is only a suggestion for the first registration; once an
        entity is in the registry, Home Assistant keeps its existing entity_id.
        """
        self._attr_unique_id = f"{self.entry.entry_id}_{key}"
        if platform is not None:
            self.entity_id = f"{platform}.{slugify(self.karotz_name)}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return per-entry device info."""
        suffix = DEVICE_NAME_SUFFIXES.get(self.device_id, "")
        info: DeviceInfo = {
            "identifiers": {(DOMAIN, f"{self.entry.entry_id}_{self.device_id}")},
            "name": f"{self.karotz_name} {suffix}".strip(),
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }
        # Entry unique_id is the formatted WLAN MAC (when known).
        if self.device_id == DEVICE_KAROTZ and self.entry.unique_id:
            info["connections"] = {(CONNECTION_NETWORK_MAC, self.entry.unique_id)}
        return info
