"""Support for fenotek sensors."""

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
from .fenotek_api.notification import Notification


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensor entities from a config_entry."""
    coordinator: FenotekDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    for doorbell in coordinator.fenotek_account.doorbells:
        for dry_contact in doorbell.dry_contacts:
            async_add_entities(
                [FenotekSensor(coordinator, hass, doorbell, dry_contact.name)]
            )


class FenotekSensor(CoordinatorEntity, SensorEntity):
    """Implementation of datetime sensors repesenting last dry contact activator."""

    # _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _last_notif: Notification | None = None

    def __init__(
        self,
        coordinator: FenotekDataUpdateCoordinator,
        hass: HomeAssistant,
        doorbell: Doorbell,
        dry_contact_name: str,
    ) -> None:
        """Initialize the datetime sensor."""
        super().__init__(coordinator)
        SensorEntity.__init__(self)
        self._doorbell = doorbell
        self._dry_contact_name = dry_contact_name

        self._attr_unique_id = f"{doorbell.id_}-{dry_contact_name}-last-activation"

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
        self._set_value()

    @property
    def available(self) -> bool:
        """Get current availability."""
        return self._doorbell.available

    def _set_value(self) -> None:
        """Set value."""
        notifs = [
            n for n in self._doorbell.activations if n.label == self._dry_contact_name
        ]
        if notifs:
            self._last_notif = notifs[-1]
            self._attr_native_value = self._last_notif.created_at

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._set_value()
        self.async_write_ha_state()
        super()._handle_coordinator_update()
