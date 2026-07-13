"""Plateforme image pour l'intégration OpenKarotz."""

from __future__ import annotations

import asyncio
import logging
import socket
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_NAME, FILENAME, SNAPSHOT_SELECT_ENTITY, SNAPSHOT_URL_TEMPLATE
from .image_entity import KarotzImage

if TYPE_CHECKING:
    from homeassistant.core import Event
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30


def _write_bytes(path: str, data: bytes) -> None:
    """Écriture fichier en mode bloquant (exécutée dans un executor)."""
    with Path(path).open("wb") as f:
        f.write(data)


async def _async_update_image(
    hass: HomeAssistant,
    config: ConfigType,
    image_path: str,
) -> bytes | None:
    """
    Télécharge le snapshot sélectionné dans select.openkarotz_snapshots.

    Appelé soit au démarrage, soit à chaque changement du select.
    Si le select n'est pas encore disponible ou si le téléchargement échoue,
    le fichier existant est conservé.
    """
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

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
            last_error = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    async with session.get(img_url, timeout=timeout) as resp:
                        if resp.status == HTTPStatus.OK:
                            data = await resp.read()
                            break
                        last_error = f"HTTP {resp.status}"
                        _LOGGER.warning(
                            "Échec téléchargement (tentative %s) : %s",
                            attempt,
                            last_error,
                        )
                except (TimeoutError, aiohttp.ClientError, socket.gaierror) as err:
                    last_error = str(err)
                    _LOGGER.debug("Tentative %s échouée : %s", attempt, err)

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** (attempt - 1))
                else:
                    _LOGGER.error(
                        "Impossible de télécharger après %s tentatives : %s",
                        MAX_RETRIES,
                        last_error,
                    )

            if data:
                await hass.async_add_executor_job(_write_bytes, image_path, data)
                _LOGGER.info("Snapshot téléchargé : %s", img_url)
                return data
            _LOGGER.info("Fichier image conservé (téléchargement échoué).")

    except Exception:
        _LOGGER.exception("Erreur lors du téléchargement de l'image Karotz")

    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # noqa: ARG001
) -> None:
    """Configure la plateforme image et son coordinator."""
    image_path = hass.config.path(f"www/{FILENAME}")
    Path(image_path).parent.mkdir(parents=True, exist_ok=True)

    # Pas de polling — update_interval=None, on pilote manuellement via l'event
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="karotz_image",
        update_method=lambda: _async_update_image(hass, config, image_path),
        update_interval=None,
    )

    # Chargement initial
    await coordinator.async_refresh()
    _LOGGER.debug("Image path : %s", image_path)

    entity = KarotzImage(hass, coordinator, image_path, None, DEFAULT_NAME)
    async_add_entities([entity])

    # Écouter les changements du select et déclencher le coordinator immédiatement
    @callback
    def _on_snapshot_selected(event: Event) -> None:
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
