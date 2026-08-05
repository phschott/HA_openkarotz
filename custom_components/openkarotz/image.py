"""Plateforme image pour l'intégration OpenKarotz."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .const import DOMAIN, SNAPSHOT_SLOT_COUNT
from .image_entity import KarotzSnapshotSlotImage

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,  # noqa: ARG001
) -> None:
    """
    Configure les entités image de la galerie de snapshots.

    Une entité « slot » par photo (slot 1 = snapshot le plus récent), alimentée
    par le cache local du fast coordinator et servie par Home Assistant.
    """
    snapshot_coordinator = hass.data[DOMAIN][config.entry_id]["snapshot_coordinator"]

    async_add_entities(
        KarotzSnapshotSlotImage(hass, snapshot_coordinator, index)
        for index in range(SNAPSHOT_SLOT_COUNT)
    )
