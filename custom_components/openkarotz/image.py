import logging
import os
import asyncio
import socket
from datetime import timedelta
import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.event import async_track_state_change_event

from .const import FILENAME, DEFAULT_NAME, SNAPSHOT_SELECT_ENTITY, SNAPSHOT_URL_TEMPLATE
from .image_entity import KarotzImage

_LOGGER = logging.getLogger(__name__)


def _write_bytes(path: str, data: bytes) -> None:
    """Écriture fichier en mode bloquant (exécutée dans un executor)."""
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
        """Télécharge le snapshot sélectionné dans select.openkarotz_snapshots.

        Appelé soit au démarrage, soit à chaque changement du select.
        Si le select n'est pas encore disponible ou si le téléchargement échoue,
        le fichier existant est conservé.
        """
        timeout = aiohttp.ClientTimeout(total=30)
        max_retries = 3

        # 1. Lire le nom du snapshot depuis le select
        select_state = hass.states.get(SNAPSHOT_SELECT_ENTITY)
        if select_state is None or select_state.state in ("unknown", "unavailable", ""):
            _LOGGER.warning(
                "Select '%s' pas encore disponible — mise à jour image ignorée.",
                SNAPSHOT_SELECT_ENTITY,
            )
            return None

        snapshot_filename = select_state.state
        _LOGGER.debug("Snapshot sélectionné : %s", snapshot_filename)

        # 2. Construire l'URL
        host = config.data["host"]
        img_url = SNAPSHOT_URL_TEMPLATE.format(host=host, filename=snapshot_filename)
        _LOGGER.debug("Téléchargement depuis : %s", img_url)

        # 3. Télécharger avec retries
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
                                    "Échec téléchargement (tentative %s) : HTTP %s",
                                    attempt, resp.status,
                                )
                                raise aiohttp.ClientError(f"HTTP {resp.status}")
                    except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror) as err:
                        _LOGGER.debug("Tentative %s échouée : %s", attempt, err)
                        if attempt < max_retries:
                            await asyncio.sleep(2 ** (attempt - 1))
                        else:
                            _LOGGER.error(
                                "Impossible de télécharger après %s tentatives : %s",
                                max_retries, err,
                            )

                if data:
                    await hass.async_add_executor_job(_write_bytes, image_path, data)
                    _LOGGER.info("Snapshot téléchargé : %s", img_url)
                    return data
                else:
                    _LOGGER.info("Fichier image conservé (téléchargement échoué).")

        except Exception as e:
            _LOGGER.error("Erreur lors du téléchargement de l'image Karotz : %s", e)

        return None

    # Pas de polling — update_interval=None, on pilote manuellement via l'event
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="karotz_image",
        update_method=update_image,
        update_interval=None,
    )

    # Chargement initial
    await coordinator.async_refresh()
    _LOGGER.debug("Image path : %s", image_path)

    entity = KarotzImage(hass, coordinator, image_path, None, DEFAULT_NAME)
    async_add_entities([entity])

    # Écouter les changements du select et déclencher le coordinator immédiatement
    @callback
    def _on_snapshot_selected(event) -> None:
        """Appelé dès que l'utilisateur change la valeur du select."""
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")

        # Ignorer si l'état est invalide
        if new_state is None or new_state.state in ("unknown", "unavailable", ""):
            return
        # Ignorer si la valeur n'a pas changé (ex: simple refresh d'attributs)
        if old_state is not None and new_state.state == old_state.state:
            return

        _LOGGER.debug(
            "Snapshot changé : %s → %s",
            old_state.state if old_state else "—",
            new_state.state,
        )
        # Déclencher le refresh du coordinator (non bloquant)
        hass.async_create_task(coordinator.async_refresh())

    async_track_state_change_event(
        hass,
        [SNAPSHOT_SELECT_ENTITY],
        _on_snapshot_selected,
    )