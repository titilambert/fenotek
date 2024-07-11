"""Support for the Environment Canada radar imagery."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FenotekDataUpdateCoordinator
from .fenotek_api.doorbell import Doorbell
from .fenotek_api.notification import NotificationSubType


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add a weather entity from a config_entry."""
    coordinator: FenotekDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    for doorbell in coordinator.fenotek_account.doorbells:
        for dry_contact in doorbell.dry_contacts:
            async_add_entities(
                [FenotekSensor(coordinator, hass, doorbell, dry_contact.name)]
            )


class FenotekSensor(CoordinatorEntity, SensorEntity):
    """Implementation of an Environment Canada radar camera."""

    # _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: FenotekDataUpdateCoordinator,
        hass: HomeAssistant,
        doorbell: Doorbell,
        dry_contact_name: str,
    ) -> None:
        """Initialize the camera."""
        super().__init__(coordinator)
        SensorEntity.__init__(self)
        self._doorbell = doorbell
        self._dry_contact_name = dry_contact_name

        # self.radar_object = coordinator.ec_data
        self._attr_unique_id = f"{doorbell.id_}-{dry_contact_name}-last-activation"
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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        notifs = [
            n
            for n in self._doorbell.notifications
            if n.sub_type == NotificationSubType.ACTIVATION
            and n.label == self._dry_contact_name
        ]
        if notifs:
            self._attr_native_value = notifs[-1].created_at
        super()._handle_coordinator_update()
