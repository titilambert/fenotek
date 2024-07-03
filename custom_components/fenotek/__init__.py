"""Fenotek HA integration root module."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client

from .const import CONF_TIMEZONE, DOMAIN
from .coordinator import FenotekDataUpdateCoordinator
from .fenotek_api.account import FenotekAccount
from .fenotek_api.doorbell import Doorbell

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=20)
# PLATFORMS = [Platform.CAMERA, Platform.BUTTON]
PLATFORMS = [Platform.IMAGE, Platform.NUMBER, Platform.BUTTON]

_LOGGER = logging.getLogger(__name__)


@dataclass
class HomeAssistantFenotekData:
    """Fenotek data stored in the Home Assistant data object."""

    coordinator: FenotekDataUpdateCoordinator
    platforms: defaultdict[Platform, list[Doorbell]]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up EC as config entry."""
    username: str = config_entry.data[CONF_USERNAME]
    password: str = config_entry.data[CONF_PASSWORD]
    timezone: str = config_entry.data[CONF_TIMEZONE]

    websession = aiohttp_client.async_get_clientsession(hass)

    fenotek_account = FenotekAccount(
        username=username,
        password=password,
        timezone=timezone,
        websession=websession,
    )

    connected = await fenotek_account.login()
    if not connected:
        _LOGGER.warning("Unable to connect to fenotek")
        raise ConfigEntryNotReady

    await fenotek_account.get_doorbells()

    coordinator: FenotekDataUpdateCoordinator = FenotekDataUpdateCoordinator(
        hass, fenotek_account, username, DEFAULT_UPDATE_INTERVAL
    )
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    #    for doorbell in fenotek_account.doorbells:
    #        _LOGGER.debug("Added doorbell (%s)", doorbell)
    #        await doorbell.update()
    #
    #        device_registry.async_get_or_create(
    #            config_entry_id=config_entry.entry_id,
    #            connections=doorbell.connections,
    #            identifiers={(DOMAIN, doorbell.identifiers)},
    #            name=doorbell.name,
    #            manufacturer=doorbell.manufacturer,
    #            model=doorbell.model,
    #            hw_version=doorbell.hw_version,
    #            sw_version=doorbell.sw_version,
    #        )

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True
