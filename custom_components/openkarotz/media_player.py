"""Media player entity for OpenKarotz integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.media_player import MediaPlayerEntity

if TYPE_CHECKING:
    from .api import KarotzAPI


class KarotzMediaPlayer(MediaPlayerEntity):
    """Media player entity backed by the OpenKarotz sound API."""

    def __init__(self, api: KarotzAPI) -> None:
        """Initialize the media player with the API client."""
        self.api = api

    async def async_play_media(
        self,
        media_type: str,  # noqa: ARG002
        media_id: str,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Play media from a URL."""
        await self.api.sound_url(media_id)

    async def async_media_pause(self) -> None:
        """Pause playback."""
        await self.api.sound_pause()

    async def async_media_stop(self) -> None:
        """Stop playback."""
        await self.api.sound_quit()
