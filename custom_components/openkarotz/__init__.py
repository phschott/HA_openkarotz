"""OpenKarotz integration for Home Assistant."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KarotzAPI
from .const import DEVICE_NAME_SUFFIXES, DOMAIN, PLATFORMS
from .coordinator import FastCoordinator, KarotzCoordinator, SnapshotCoordinator
from .shared_state import KarotzSharedState

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Prefix of the global (pre-2) unique_ids, e.g. "openkarotz_led_pulse".
_LEGACY_UNIQUE_ID_PREFIX = "openkarotz_"
# Global (pre-2) device identifiers.
_LEGACY_DEVICE_IDS = frozenset(DEVICE_NAME_SUFFIXES)


def _install_blueprints(hass: HomeAssistant) -> None:
    """Copy bundled blueprints to the HA config directory (skip if already present)."""
    src = Path(__file__).parent / "blueprints"
    dest = Path(hass.config.config_dir) / "blueprints" / "automation" / "openkarotz"
    dest.mkdir(parents=True, exist_ok=True)
    for blueprint in src.glob("*.yaml"):
        target = dest / blueprint.name
        if not target.exists():
            shutil.copy2(blueprint, target)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenKarotz integration from config entry."""
    await hass.async_add_executor_job(_install_blueprints, hass)

    # Initialize API client with Home Assistant's shared aiohttp session
    api = KarotzAPI(entry.data["host"], async_get_clientsession(hass))

    # Initialize coordinators
    coordinator = KarotzCoordinator(hass, entry, api)
    fast_coordinator = FastCoordinator(hass, entry, api)
    snapshot_coordinator = SnapshotCoordinator(hass, entry, api)

    # Perform initial data refresh (snapshots load once here, then on demand)
    await coordinator.async_config_entry_first_refresh()
    await fast_coordinator.async_config_entry_first_refresh()
    await snapshot_coordinator.async_config_entry_first_refresh()

    _async_backfill_unique_id(hass, entry, fast_coordinator.data)

    # Store data in hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "fast_coordinator": fast_coordinator,
        "snapshot_coordinator": snapshot_coordinator,
        "shared_state": KarotzSharedState(),
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OpenKarotz config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


@callback
def _async_backfill_unique_id(
    hass: HomeAssistant, entry: ConfigEntry, fast_data: dict | None
) -> None:
    """
    Give entries created before 1.5.0 the WLAN MAC as unique_id.

    Lets the config flow refuse adding the same Karotz twice, also for entries
    that were created before the flow read the MAC.
    """
    if entry.unique_id is not None:
        return
    status = (fast_data or {}).get("status") or {}
    mac = status.get("wlan_mac")
    if not mac:
        return
    unique_id = dr.format_mac(mac)
    if any(
        other.unique_id == unique_id
        for other in hass.config_entries.async_entries(DOMAIN)
        if other.entry_id != entry.entry_id
    ):
        _LOGGER.warning(
            "Karotz %s (%s) is configured more than once; remove the duplicate entry",
            unique_id,
            entry.data.get("host"),
        )
        return
    hass.config_entries.async_update_entry(entry, unique_id=unique_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate an old config entry."""
    if entry.version > 2:  # noqa: PLR2004
        # Downgrade from a future version: not supported.
        return False

    if entry.version == 1:
        await _async_migrate_v1_to_v2(hass, entry)
        hass.config_entries.async_update_entry(entry, version=2)
        _LOGGER.info("Migrated OpenKarotz entry %s to version 2", entry.entry_id)

    return True


async def _async_migrate_v1_to_v2(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """
    Scope entity unique_ids and device identifiers to the config entry.

    Version 1 used global ids ("openkarotz_led_pulse", device "karotz_leds"),
    so a second Karotz collided with the first. Only the unique_id and device
    identifiers change; entity_ids (and so history, dashboards and
    automations) are kept.
    """
    prefix = entry.entry_id

    @callback
    def _migrate_entity(reg_entry: er.RegistryEntry) -> dict[str, str] | None:
        if not reg_entry.unique_id.startswith(_LEGACY_UNIQUE_ID_PREFIX):
            return None
        key = reg_entry.unique_id.removeprefix(_LEGACY_UNIQUE_ID_PREFIX)
        return {"new_unique_id": f"{prefix}_{key}"}

    await er.async_migrate_entries(hass, entry.entry_id, _migrate_entity)

    dev_reg = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(dev_reg, entry.entry_id):
        has_legacy = any(
            domain == DOMAIN and ident in _LEGACY_DEVICE_IDS
            for domain, ident in device.identifiers
        )
        if _device_owner(device) not in (None, entry.entry_id) or not has_legacy:
            # Device belongs to another Karotz entry (or was already migrated
            # by it) and was only shared with this one because of the old
            # global identifiers: detach it. This entry recreates its own
            # devices on setup. Newer HA cores give every device a single
            # config entry, so this cannot happen there.
            dev_reg.async_update_device(
                device.id, remove_config_entry_id=entry.entry_id
            )
            continue
        dev_reg.async_update_device(
            device.id,
            new_identifiers={
                (domain, f"{prefix}_{ident}")
                if domain == DOMAIN and ident in _LEGACY_DEVICE_IDS
                else (domain, ident)
                for domain, ident in device.identifiers
            },
        )


def _device_owner(device: dr.DeviceEntry) -> str | None:
    """
    Return the config entry that owns a device, across HA core versions.

    Newer cores give a device a single ``config_entry_id`` and deprecate
    ``primary_config_entry``; older ones (multi-entry devices) only have the
    latter.
    """
    if hasattr(device, "config_entry_id"):
        return device.config_entry_id
    return device.primary_config_entry
