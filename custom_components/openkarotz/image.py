import logging
import os
import asyncio
import socket
from datetime import timedelta
import aiohttp
import xml.etree.ElementTree as ET
import re

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util

from .const import FILENAME, DEFAULT_NAME, DOMAIN
from .image_entity import KarotzImage

_LOGGER = logging.getLogger(__name__)

# Helper to perform blocking file write on executor
def _write_bytes(path: str, data: bytes) -> None:
    with open(path, "wb") as f:
        f.write(data)

async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
):
    image_path = hass.config.path(f"www/{FILENAME}")
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    async def update_image():
        """Download latest comic from RSS feed with retries and timeout.
        If download fails, keep existing file (do not overwrite with empty data)."""
        timeout = aiohttp.ClientTimeout(total=30)
        max_retries = 3
        try:
            async with aiohttp.ClientSession() as session:
                
                img_url = "http://192.168.1.170/cgi-bin/snapshot_get?filename=snapshot_2026_05_15_12_31_00.jpg"

                if not img_url:
                    _LOGGER.warning("No image URL found in latest feed item")
                    return None

                # Download the image (with retries)
                data = None
                for attempt in range(1, max_retries + 1):
                    try:
                        async with session.get(img_url, timeout=timeout) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                break
                            else:
                                _LOGGER.warning("Failed to download image (attempt %s): HTTP %s", attempt, resp.status)
                                raise aiohttp.ClientError(f"HTTP {resp.status}")
                    except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror) as err:
                        _LOGGER.debug("Image download attempt %s failed: %s", attempt, err)
                        if attempt < max_retries:
                            await asyncio.sleep(2 ** (attempt - 1))
                        else:
                            _LOGGER.error("Failed to download image after %s attempts: %s", max_retries, err)

                if data:
                    # Write file on executor to avoid blocking the event loop
                    await hass.async_add_executor_job(_write_bytes, image_path, data)
                    _LOGGER.info("Downloaded Karotz image: %s", img_url)
                    return data
                else:
                    _LOGGER.info("Keeping existing image file (download failed).")
        except Exception as e:
            _LOGGER.error("Failed to download Karotz image: %s", e)
        return None

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="karotz_image",
        update_method=update_image,
        update_interval=timedelta(seconds=10),  # fallback for platform setup
    )

    await coordinator.async_refresh()
    # When created from platform (legacy) we can't tie to a config entry;
    # use None for config_entry_id so unique_id is based on feed filename.
    _LOGGER.warning("Path: %s", image_path)
    async_add_entities([KarotzImage(hass, coordinator, image_path, None, DEFAULT_NAME)])
