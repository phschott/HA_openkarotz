import logging
import os
import asyncio
import socket
from datetime import timedelta
import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import FILENAME, DEFAULT_NAME, SNAPSHOT_SELECT_ENTITY, SNAPSHOT_URL_TEMPLATE
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
        """Download latest snapshot from the Karotz device.

        The snapshot filename is read dynamically from the select entity
        (select.openkarotz_snapshots). If the select has no state yet,
        or if the download fails, the existing file is kept as-is.
        """
        timeout = aiohttp.ClientTimeout(total=30)
        max_retries = 3

        # ------------------------------------------------------------------ #
        # 1. Resolve the snapshot filename from the select entity             #
        # ------------------------------------------------------------------ #
        select_state = hass.states.get(SNAPSHOT_SELECT_ENTITY)
        if select_state is None or select_state.state in ("unknown", "unavailable", ""):
            _LOGGER.warning(
                "Select entity '%s' is not available yet — skipping image update.",
                SNAPSHOT_SELECT_ENTITY,
            )
            return None

        snapshot_filename = select_state.state  # e.g. "snapshot_2026_05_15_12_31_00.jpg"
        _LOGGER.debug("Selected snapshot filename: %s", snapshot_filename)

        # ------------------------------------------------------------------ #
        # 2. Build the URL                                                    #
        #    Le host est lu directement depuis la config entry (saisi par     #
        #    l'utilisateur dans config_flow.py et persisté par HA).           #
        # ------------------------------------------------------------------ #
        host = config.data["host"]
        img_url = SNAPSHOT_URL_TEMPLATE.format(host=host, filename=snapshot_filename)
        _LOGGER.debug("Downloading snapshot from: %s", img_url)

        # ------------------------------------------------------------------ #
        # 3. Download the image with retries                                  #
        # ------------------------------------------------------------------ #
        try:
            async with aiohttp.ClientSession() as session:
                data = None
                for attempt in range(1, max_retries + 1):
                    try:
                        async with session.get(img_url, timeout=timeout) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                break
                            else:
                                _LOGGER.warning(
                                    "Failed to download image (attempt %s): HTTP %s",
                                    attempt,
                                    resp.status,
                                )
                                raise aiohttp.ClientError(f"HTTP {resp.status}")
                    except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror) as err:
                        _LOGGER.debug("Image download attempt %s failed: %s", attempt, err)
                        if attempt < max_retries:
                            await asyncio.sleep(2 ** (attempt - 1))
                        else:
                            _LOGGER.error(
                                "Failed to download image after %s attempts: %s",
                                max_retries,
                                err,
                            )

                if data:
                    # Write file on executor to avoid blocking the event loop
                    await hass.async_add_executor_job(_write_bytes, image_path, data)
                    _LOGGER.info("Downloaded Karotz snapshot: %s", img_url)
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
    _LOGGER.warning("Path: %s", image_path)
    async_add_entities([KarotzImage(hass, coordinator, image_path, None, DEFAULT_NAME)])