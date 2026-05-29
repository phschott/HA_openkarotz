"""OpenKarotz integration for Home Assistant."""

from typing import TYPE_CHECKING

from .api import KarotzAPI
from .const import DOMAIN, FILENAME, PLATFORMS
from .coordinator import FastCoordinator, KarotzCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenKarotz integration from config entry."""
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
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
