"""Image entity for OpenKarotz integration."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.image import ImageEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class KarotzImage(CoordinatorEntity, ImageEntity):
    """Image entity exposing the latest OpenKarotz snapshot."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        path: str,
        config_entry_id: str | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize the image entity."""
        # Initialize CoordinatorEntity so the entity receives coordinator updates
        super().__init__(coordinator)
        self.hass = hass
        self.coordinator = coordinator
        self._path = path
        self._config_entry_id = config_entry_id
        # do not set a fixed entity_id — let HA assign one based on name/unique_id

        # minimal access token support required by the image component
        # generate a stable token per entity instance (sufficient for local testing)
        self._access_token = uuid.uuid4().hex
        self._access_tokens = [self._access_token]

        # keep a stable unique id per config entry (or per filename when no entry)
        # This makes Home Assistant reuse the same registry entry and link it
        # to the integration
        if config_entry_id:
            self._unique_id = f"{DOMAIN}_{config_entry_id}"
        else:
            # fallback unique id based on filename path
            self._unique_id = f"{DOMAIN}_{Path(self._path).name}"

        self._name = name or DEFAULT_NAME
        self.device_id = "karotz_picture"
        # Timestamp when the image was last refreshed (timezone-aware UTC datetime)
        self._last_refreshed: datetime | None = None
        # Publication date of the comic (datetime object from RSS feed)
        self._pub_date: datetime | None = None

    async def async_added_to_hass(self) -> None:
        """Register a listener to rotate the access token when coordinator updates."""
        # coordinator.async_add_listener returns an unsubscribe callable
        self._remove_coordinator_listener = self.coordinator.async_add_listener(
            self._on_coordinator_update
        )

        # Initialize last_refreshed only if the coordinator already has data
        # (first successful refresh). update_method returns a dict with image_data
        # and pub_date when a new image was fetched, and None when nothing changed;
        # this avoids updating the timestamp on empty refreshes.
        if getattr(self.coordinator, "data", None) is not None:
            # Prefer coordinator-provided timestamps if available, otherwise use now
            coordinator_time = None
            for attr in (
                "last_update_time",
                "last_update_at",
                "last_update",
                "_last_update",
                "_last_update_time",
                "_last_update_at",
            ):
                coordinator_time = getattr(self.coordinator, attr, None)
                if isinstance(coordinator_time, datetime):
                    break
            self._last_refreshed = coordinator_time or dt_util.utcnow()
            # Extract and parse publication date from coordinator data
            if isinstance(self.coordinator.data, dict):
                pub_date_str = self.coordinator.data.get("pub_date")
                if pub_date_str:
                    try:
                        self._pub_date = parsedate_to_datetime(pub_date_str)
                    except Exception as e:  # noqa: BLE001
                        _LOGGER.debug(
                            "Failed to parse publication date '%s': %s", pub_date_str, e
                        )
        else:
            self._last_refreshed = None

    async def async_will_remove_from_hass(self) -> None:
        if hasattr(self, "_remove_coordinator_listener") and callable(
            self._remove_coordinator_listener
        ):
            self._remove_coordinator_listener()

    def _on_coordinator_update(self) -> None:
        """Rotate access token and write state so the frontend reloads the image."""
        self._access_token = uuid.uuid4().hex
        self._access_tokens = [self._access_token]
        # Update last refreshed timestamp only when coordinator has non-None data
        # (update_image returns dict when a new image was actually downloaded)
        if getattr(self.coordinator, "data", None) is not None:
            self._last_refreshed = dt_util.utcnow()
            # Extract and parse publication date from coordinator data
            if isinstance(self.coordinator.data, dict):
                pub_date_str = self.coordinator.data.get("pub_date")
                if pub_date_str:
                    try:
                        self._pub_date = parsedate_to_datetime(pub_date_str)
                    except Exception as e:  # noqa: BLE001
                        _LOGGER.debug(
                            "Failed to parse publication date '%s': %s", pub_date_str, e
                        )
        # Trigger HA state update so frontend will use the new token/url
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes for the entity."""
        attrs = {}
        if self._last_refreshed:
            try:
                attrs["last_updated"] = dt_util.as_utc(self._last_refreshed).isoformat()
            except Exception:  # noqa: BLE001
                attrs["last_updated"] = str(self._last_refreshed)
        return attrs

    @property
    def state(self) -> datetime | None:
        """
        Return the entity state.

        Return the full publication datetime from the RSS feed.
        Home Assistant will format it according to user's locale.
        """
        return self._pub_date

    def _read_file(self) -> bytes:
        with Path(self._path).open("rb") as f:
            return f.read()

    async def async_image(self) -> bytes | None:
        """Return image bytes, reading the file on an executor thread."""
        try:
            return await self.hass.async_add_executor_job(self._read_file)
        except FileNotFoundError:
            return None
        except Exception:
            _LOGGER.exception("Failed to read Karotz image file")
            return None

    @property
    def access_tokens(self) -> list[str]:
        """Return access tokens used by the image helper."""
        return self._access_tokens

    @property
    def unique_id(self) -> str:
        """Return unique id for the entity (used by the entity registry)."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the entity name shown in the UI."""
        return self._name

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device information to group entities together."""
        if self._unique_id:
            return {
                "identifiers": {(DOMAIN, self.device_id)},
                "name": self._name,
                "manufacturer": MANUFACTURER,
                "model": MODEL,
            }
        return None

    @property
    def device_class(self) -> str:
        """Return device class 'timestamp' for datetime formatting with localization."""
        return "timestamp"
