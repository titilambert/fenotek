"""Doorbell module."""

from datetime import datetime

from .api_reponse import VisiophoneHomeResponse, VisiophoneResponse
from .client import FenotekClient
from .dry_contact import DryContact


class Doorbell:
    """Doorbell class."""

    _raw_data: VisiophoneResponse
    _raw_home: VisiophoneHomeResponse
    _camera_image: bytes

    def __init__(self, fenotek_client: FenotekClient, id_: str) -> None:
        """Doorbell class constructor."""
        self._fenotek_client = fenotek_client
        self.id_ = id_
        self._camera = None
        self._dry_contacts: list[DryContact] = []
        self._available = False

    async def update(self) -> None:
        """Update doorbell data."""
        self._raw_data = await self._fenotek_client.get_doorbell(self.id_)
        self._raw_home = await self._fenotek_client.home(self.id_)
        self._camera_image = await self._fenotek_client.fetch_camera_image(
            self._raw_home["lastNotification"]["detail"]["url"]
        )
        if not self._dry_contacts:
            for dry_contact_data in self._raw_data["dryContacts"]:
                self._dry_contacts.append(
                    DryContact(self._fenotek_client, self.id_, dry_contact_data)
                )

    async def ping(self) -> bool:
        """Doorbell ping."""
        self._available = await self._fenotek_client.ping(self.id_)
        return self._available

    @property
    def available(self) -> bool:
        """Doorbell available."""
        return self._available

    @property
    def dry_contacts(self) -> list[DryContact]:
        """Doorbell dry contacts."""
        return self._dry_contacts

    @property
    def connections(self) -> set[tuple[str, str]]:
        """Doorbell connections."""
        return {(self._raw_data["connectionType"], self.id_)}
        # return {[self._raw_data["connectionType"], self.id_]}

    @property
    def identifiers(self) -> str:
        """Doorbell id."""
        return self.id_

    @property
    def name(self) -> str:
        """Doorbell name."""
        return self._raw_data["description"]

    @property
    def manufacturer(self) -> str:
        """Doorbell Manufacturer."""
        return "CDVI"

    @property
    def model(self) -> str:
        """Doorbell model."""
        return "Hi)"

    @property
    def hw_version(self) -> str:
        """Doorbell hardware version."""
        return f"{self._raw_data['major']}.{self._raw_data['minor']}"

    @property
    def sw_version(self) -> str:
        """Doorbell software version."""
        return self._raw_data["hiVersion"]

    @property
    def last_notification_url(self) -> str:
        """Last notification url."""
        return self._raw_home["lastNotification"]["detail"]["url"]

    @property
    def last_notification_date(self) -> datetime:
        """Last notification date."""
        date_str = self._raw_home["lastNotification"]["createdAt"].split(".")[0]
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

    @property
    def last_notification_type(self) -> str:
        """Last notification type."""
        type_id = self._raw_home["lastNotification"]["detail"]["type"]
        type_mapping = {
            0: "ZERO",
        }
        return type_mapping.get(type_id, f"unknown - {type_id}")

    @property
    def last_notification_image(self) -> bytes | None:
        """Last notification image."""
        return self._camera_image
