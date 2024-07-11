"""Support for the Environment Canada radar imagery."""

from __future__ import annotations

from homeassistant.components import ffmpeg
from homeassistant.components.camera import (
    Camera,
    CameraEntityDescription,
    CameraEntityFeature,
)
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


IMAGE_TYPE = CameraEntityDescription(  # type: ignore[call-arg]
    key="last_motion_image",
    translation_key="last_motion_image",
)


class FenotekCamera(CoordinatorEntity, Camera):
    # class FenotekCamera(CoordinatorEntity, Camera):
    """Implementation of an Environment Canada radar camera."""

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

        # self.radar_object = coordinator.ec_data
        # self._attr_unique_id = f"{doorbell.id_}-camera"
        # self._attr_attribution = self.radar_object.metadata["attribution"]
        # self._attr_entity_registry_enabled_default = False

        device_info = DeviceInfo(
            # config_entry_id=coordinator.config_entry.entry_id,
            connections=doorbell.connections,
            identifiers={(DOMAIN, doorbell.identifiers)},
            name=doorbell.name,
            manufacturer=doorbell.manufacturer,
            model=doorbell.model,
            hw_version=doorbell.hw_version,
            sw_version=doorbell.sw_version,
        )

        self._attr_device_info = device_info

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

    @callback
    def _handle_coordinator_update(self) -> None:
        if self._last_notif:
            self._attr_extra_state_attributes["last_update"] = (
                self._last_notif.created_at
            )
        super()._handle_coordinator_update()


class FenotekCameraLastEvent(FenotekCamera):
    """Last event camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-last-event"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._last_notif = self._doorbell.last_notification
        self.async_write_ha_state()
        super()._handle_coordinator_update()


class FenotekCameraMotion(FenotekCamera):
    """Last motion camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-motion"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._last_notif = self._doorbell.last_motion
        self.async_write_ha_state()
        super()._handle_coordinator_update()


class FenotekCameraMissedCall(FenotekCamera):
    """Last missed call camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-missedcall"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle new data."""
        self._last_notif = self._doorbell.last_missed_call
        self.async_write_ha_state()
        super()._handle_coordinator_update()


class FenotekCameraAnsweredCall(FenotekCamera):
    """Last answered call camera."""

    @property
    def unique_id(self) -> str:
        """Return camera name."""
        return f"{self._doorbell.id_}-camera-answeredcall"

    @callback
    def _handle_coordinator_update(self) -> None:
        self._last_notif = self._doorbell.last_call
        self.async_write_ha_state()
        super()._handle_coordinator_update()
