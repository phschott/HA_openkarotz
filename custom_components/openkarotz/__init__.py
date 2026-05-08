from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .api import KarotzAPI
from .coordinator import KarotzCoordinator

# PLATFORMS = ["sensor", "light", "select", "button", "media_player"]
PLATFORMS = ["sensor", "button", "select", "text", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = KarotzAPI(entry.data["host"])
    coordinator = KarotzCoordinator(hass, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok