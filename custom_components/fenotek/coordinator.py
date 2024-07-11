"""Fenotek HA coordinator module."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .fenotek_api.account import FenotekAccount
from .fenotek_api.doorbell import Doorbell

_LOGGER = logging.getLogger(__name__)


class FenotekDataUpdateCoordinator(
    DataUpdateCoordinator
):  # pylint: disable=hass-enforce-coordinator-module
    """Class to manage fetching Fenotek data."""

    def __init__(
        self,
        hass: HomeAssistant,
        fenotek_account: FenotekAccount,
        name: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize global EC data updater."""
        super().__init__(
            hass, _LOGGER, name=f"{DOMAIN} {name}", update_interval=update_interval
        )
        self.fenotek_account: FenotekAccount = fenotek_account
        self.last_update_success: bool = False
        self._available: bool = False

    async def _async_update_data(self) -> dict[str, Doorbell]:
        """Fetch data from Fenotek."""
        ret: dict[str, Doorbell] = {}
        try:
            await self.fenotek_account.update()
        except Exception as ex:
            raise UpdateFailed(f"Error fetching {self.name} data: {ex}") from ex
        for doorbell in self.fenotek_account.doorbells:
            await doorbell.ping()
            ret[doorbell.id_] = doorbell

        return ret
