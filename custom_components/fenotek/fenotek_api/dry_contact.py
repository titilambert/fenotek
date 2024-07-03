"""Dry contact module."""

from .api_reponse import DrycontactResponse
from .client import FenotekClient


class DryContact:
    """Dry contact class."""

    def __init__(
        self,
        fenotek_client: FenotekClient,
        doorbell_id: str,
        dry_contact_data: DrycontactResponse,
    ) -> None:
        """Dry contact class constructor."""
        self._fenotek_client: FenotekClient = fenotek_client
        self._doorbell_id: str = doorbell_id
        self._raw_data: DrycontactResponse = dry_contact_data

    async def activate(self) -> bool:
        """Activate dry contact."""
        return await self._fenotek_client.trigger_drycontact(
            self._doorbell_id, self.id_
        )

    @property
    def id_(self) -> str:
        """Dry Contact ID."""
        return self._raw_data["_id"]

    @property
    def name(self) -> str:
        """Dry contact name."""
        return self._raw_data["name"]

    @property
    def command_id(self) -> str:
        """Dry contact command ID."""
        return self._raw_data["commandId"]

    @property
    def delay(self) -> int:
        """Delay in seconds to hold the contact."""
        return self._raw_data["delay"]

    @property
    def icon(self) -> str:
        """Dry contact icon letter."""
        return self._raw_data["icon"]

    @property
    def is_on_hold(self) -> bool:
        """Is dry contact activation hold contact."""
        return self._raw_data["isOnHold"]
