"""Support for Fenotek video recordings."""

from __future__ import annotations

from homeassistant.components import ffmpeg
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FenotekDataUpdateCoordinator
from .fenotek_api.doorbell import Doorbell
from .fenotek_api.notification import Notification


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a weather entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    for doorbell in coordinator.fenotek_account.doorbells:
        async_add_entities([FenotekCameraMotion(coordinator, hass, doorbell)])
        async_add_entities([FenotekCameraMissedCall(coordinator, hass, doorbell)])
        async_add_entities([FenotekCameraAnsweredCall(coordinator, hass, doorbell)])
        async_add_entities([FenotekCameraLastEvent(coordinator, hass, doorbell)])


class FenotekCamera(CoordinatorEntity, Camera):
    """Implementation of Fenotek video recording."""

    _last_notif: Notification | None = None

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_extra_state_attributes = {}

    # _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FenotekDataUpdateCoordinator,
        hass: HomeAssistant,
        doorbell: Doorbell,
    ) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        Camera.__init__(self)
        self._doorbell = doorbell
        self._image: bytes | None = None

        device_info = DeviceInfo(
            connections=doorbell.connections,
            identifiers={(DOMAIN, doorbell.identifiers)},
            name=doorbell.name,
            manufacturer=doorbell.manufacturer,
            model=doorbell.model,
            hw_version=doorbell.hw_version,
            sw_version=doorbell.sw_version,
        )

        self._attr_device_info = device_info
        self._set_last_notif()

    @property
    def available(self) -> bool:
        """Get current availability."""
        return self._doorbell.available

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        stream_source = await self.stream_source()
        if not stream_source:
            return None
        image = await ffmpeg.async_get_image(
            self.hass,
            stream_source,
            width=width,
            height=height,
        )
        if image:
            self._image = image
        return self._image

    async def stream_source(self) -> str | None:
        """Return the source of the stream."""
        if not self._last_notif:
            return None
        return self._last_notif.video_url

    def _set_last_notif(self) -> None:
        """Save last notification."""
        raise NotImplementedError

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        if self._last_notif:
            self._attr_extra_state_attributes["last_update"] = (
                self._last_notif.created_at
            )
        self.async_write_ha_state()
        super()._handle_coordinator_update()


class FenotekCameraLastEvent(FenotekCamera):
    """Last event camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-last-event"

    def _set_last_notif(self) -> None:
        """Save last notification."""
        notifs_with_video = [n for n in self._doorbell.notifications if n.video_url]
        if not notifs_with_video:
            return None
        self._last_notif = notifs_with_video[-1]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._set_last_notif()
        super()._handle_coordinator_update()


class FenotekCameraMotion(FenotekCamera):
    """Last motion camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-motion"

    def _set_last_notif(self) -> None:
        """Save last notification."""
        self._last_notif = self._doorbell.last_motion

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._set_last_notif()
        super()._handle_coordinator_update()


class FenotekCameraMissedCall(FenotekCamera):
    """Last missed call camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-missedcall"

    def _set_last_notif(self) -> None:
        """Save last notification."""
        self._last_notif = self._doorbell.last_missed_call

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._set_last_notif()
        super()._handle_coordinator_update()


class FenotekCameraAnsweredCall(FenotekCamera):
    """Last answered call camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-answeredcall"

    def _set_last_notif(self) -> None:
        """Save last notification."""
        self._last_notif = self._doorbell.last_call

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._set_last_notif()
        super()._handle_coordinator_update()
