"""Support for the Environment Canada radar imagery."""

from __future__ import annotations

import datetime

from homeassistant.components.number import (
    NumberEntityDescription,
    NumberExtraStoredData,
    NumberMode,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
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
    """Add a weather entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    for doorbell in coordinator.fenotek_account.doorbells:
        async_add_entities([FenotekNumber(coordinator, doorbell)])


class FenotekNumber(CoordinatorEntity, RestoreNumber):
    """Implementation of an Environment Canada radar camera."""

    # _attr_has_entity_name = True

    def __init__(
        self, coordinator: FenotekDataUpdateCoordinator, doorbell: Doorbell
    ) -> None:
        """Initialize the camera."""
        self.restored_data: NumberExtraStoredData | None = None
        super().__init__(coordinator)
        RestoreNumber.__init__(self)
        self._doorbell = doorbell

        # self.radar_object = coordinator.ec_data
        self._attr_unique_id = f"{doorbell.id_}-update-interval"
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
        self._attr_native_max_value = 120
        self._attr_native_min_value = 1
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX
        self.native_unit_of_measurement = "seconds"
        self.entity_description = NumberEntityDescription(  # type: ignore[call-arg]
            key="update_interval",
            translation_key="update_interval",
        )

    @property
    def native_value(self) -> float | None:
        """Get actual value."""
        if self.restored_data is not None:
            return self.restored_data.native_value
        return None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        self.restored_data = await self.async_get_last_number_data()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        assert self.restored_data is not None
        self.restored_data.native_value = int(value)
        self.coordinator.update_interval = datetime.timedelta(
            seconds=self.restored_data.native_value
        )
        self.async_write_ha_state()
        await self.coordinator.async_refresh()
