"""Fenotek account module."""

import logging

from aiohttp import ClientSession

from .client import FenotekClient
from .doorbell import Doorbell


class FenotekAccount:
    """Fenotek account class."""

    def __init__(
        self,
        username: str,
        password: str,
        timezone: str,
        websession: ClientSession,
        logger: logging.Logger | None = None,
    ) -> None:
        """Fenotek account class constructor."""
        self._logger: logging.Logger = logger or logging.getLogger("fenotek")
        self._fenotek_client = FenotekClient(
            username,
            password,
            timezone,
            websession,
            self._logger.getChild("client"),
        )
        self._username = username
        self._doorbells: list[Doorbell] = []

    @property
    def username(self) -> str:
        """Fenotek account username."""
        return self._username

    async def login(self) -> bool:
        """Login to Fenotek api."""
        return await self._fenotek_client.login()

    async def get_doorbells(self) -> list[Doorbell]:
        """Get Loging to Fenotek api."""
        json_res = await self._fenotek_client.get_doorbells()
        self._doorbells = []
        for doorbell_id in json_res["visiophones"]:
            doorbell = Doorbell(self._fenotek_client, doorbell_id)
            self._doorbells.append(doorbell)
            await doorbell.update()
        return self._doorbells

    async def update(self) -> None:
        """Update all doorbells data."""
        for doorbell in self._doorbells:
            await doorbell.update()

    @property
    def doorbells(self) -> list[Doorbell]:
        """Doorbells linked to the account."""
        return self._doorbells
