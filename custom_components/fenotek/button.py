"""Support for Fenotek dry contact activation button."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ICON_MAPPING
from .coordinator import FenotekDataUpdateCoordinator
from .fenotek_api.doorbell import Doorbell
from .fenotek_api.dry_contact import DryContact


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add buttons entities from a config_entry."""
    coordinator: FenotekDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    for doorbell in coordinator.fenotek_account.doorbells:
        for dry_contact in doorbell.dry_contacts:
            async_add_entities([FenotekButton(coordinator, doorbell, dry_contact)])


class FenotekButton(CoordinatorEntity, ButtonEntity):
    """Implementation of dry contact activation button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FenotekDataUpdateCoordinator,
        doorbell: Doorbell,
        dry_contact: DryContact,
    ):
        """Initialize the button."""
        super().__init__(coordinator)
        ButtonEntity.__init__(self)
        self._dry_contact = dry_contact
        self._doorbell = doorbell

        self._attr_unique_id = f"{doorbell.id_}-{dry_contact.id_}"
        self._attr_delay = dry_contact.delay

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

        self._attr_name = f"{doorbell.id_}-{dry_contact.name}"
        self._attr_icon = ICON_MAPPING.get(dry_contact.icon, None)

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self._dry_contact.activate()
        except Exception as err:
            raise HomeAssistantError(f"Can not activate dry contact: {err}") from err

    @property
    def available(self) -> bool:
        """Button avaibility."""
        return self._doorbell.available
