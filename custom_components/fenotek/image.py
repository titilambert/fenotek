"""Fenotek image module."""

from __future__ import annotations

from homeassistant.components.image import ImageEntity, ImageEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FenotekDataUpdateCoordinator
from .fenotek_api.doorbell import Doorbell


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a ring event imaeg from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    for doorbell in coordinator.fenotek_account.doorbells:
        async_add_entities([FenotekImage(coordinator, hass, doorbell)])


IMAGE_TYPE = ImageEntityDescription(  # type: ignore[call-arg]
    key="last_motion_image",
    translation_key="last_motion_image",
)


class FenotekImage(CoordinatorEntity, ImageEntity):
    """Implementation of a ring event photo."""

    def __init__(
        self,
        coordinator: FenotekDataUpdateCoordinator,
        hass: HomeAssistant,
        doorbell: Doorbell,
    ) -> None:
        """Initialize the image."""
        super().__init__(coordinator)
        ImageEntity.__init__(self, hass)
        self._doorbell = doorbell

        self._attr_unique_id = f"{doorbell.id_}-ring"

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
        if self._doorbell.last_ring:
            self._attr_image_url = self._doorbell.last_ring.url
            self._attr_image_last_updated = self._doorbell.last_ring.created_at
        self._attr_content_type = "image/jpeg"
        self.entity_description = IMAGE_TYPE

    @property
    def available(self) -> bool:
        """Get current availability."""
        return self._doorbell.available

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        if (
            self._doorbell.last_ring
            and self._attr_image_url != self._doorbell.last_ring.url
        ):
            self._attr_image_url = self._doorbell.last_ring.url
            self._attr_image_last_updated = self._doorbell.last_ring.created_at
            self._cached_image = None
        self.async_write_ha_state()
        super()._handle_coordinator_update()
