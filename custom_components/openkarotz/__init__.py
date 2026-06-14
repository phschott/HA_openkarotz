"""OpenKarotz integration for Home Assistant."""

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from .api import KarotzAPI
from .const import DOMAIN, FILENAME, PLATFORMS
from .coordinator import FastCoordinator, KarotzCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


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
    _install_blueprints(hass)

    # Initialize API client
    api = KarotzAPI(entry.data["host"])

    # Initialize coordinators
    coordinator = KarotzCoordinator(hass, api)
    fast_coordinator = FastCoordinator(hass, api)

    # Set up image path
    image_path = hass.config.path(f"www/{FILENAME}")

    # Perform initial data refresh
    await coordinator.async_config_entry_first_refresh()
    await fast_coordinator.async_config_entry_first_refresh()

    # Store data in hass
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "fast_coordinator": fast_coordinator,
        "image_path": image_path,
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
