"""Doorbell module."""

from .api_reponse import (
    VisiophoneHomeNotificationResponse,
    VisiophoneHomeResponse,
    VisiophoneResponse,
)
from .client import FenotekClient
from .dry_contact import DryContact
from .notification import Notification, NotificationSubType


class Doorbell:
    """Doorbell class."""

    _raw_data: VisiophoneResponse
    _raw_home: VisiophoneHomeResponse
    _raw_notifications: list[VisiophoneHomeNotificationResponse]

    def __init__(self, fenotek_client: FenotekClient, id_: str) -> None:
        """Doorbell class constructor."""
        self._fenotek_client = fenotek_client
        self.id_ = id_
        self._camera = None
        self._dry_contacts: list[DryContact] = []
        self._available = False
        self._notifications: list[Notification] = []

    async def update(self) -> None:
        """Update doorbell data."""
        self._raw_data = await self._fenotek_client.get_doorbell(self.id_)
        self._raw_home = await self._fenotek_client.home(self.id_)
        self._raw_notifications = await self._fenotek_client.notifications(self.id_)
        self._notifications = []
        i = 0
        for raw_notification in self._raw_notifications:
            notification = Notification.new(self._fenotek_client, raw_notification)
            if notification.sub_type in (
                NotificationSubType.ANSWERED_CALL,
                NotificationSubType.MISSED_CALL,
            ):
                await notification.fetch_details_url()
            self._notifications.append(notification)
            i += 1
        self._notifications.sort(key=lambda x: x.created_at)

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
    def calls(self) -> list[Notification]:
        """Return all the answered call notifications."""
        return [
            notif
            for notif in self._notifications
            if notif.sub_type == NotificationSubType.ANSWERED_CALL
        ]

    @property
    def last_call(self) -> Notification | None:
        """Return the last answered call notification."""
        if self.calls:
            return self.calls[-1]
        return None

    @property
    def missed_calls(self) -> list[Notification]:
        """Return all the missed call notifications."""
        return [
            notif
            for notif in self._notifications
            if notif.sub_type == NotificationSubType.MISSED_CALL
        ]

    @property
    def last_missed_call(self) -> Notification | None:
        """Return the last missed call notification."""
        if self.missed_calls:
            return self.missed_calls[-1]
        return None

    @property
    def activations(self) -> list[Notification]:
        """Return all the activate notifications."""
        return [
            notif
            for notif in self._notifications
            if notif.sub_type == NotificationSubType.ACTIVATION
        ]

    @property
    def last_activate(self) -> Notification | None:
        """Return the last activation notification."""
        if self.activations:
            return self.activations[-1]
        return None

    @property
    def notifications(self) -> list[Notification]:
        """Return all notifications."""
        return [notif for notif in self._notifications]

    @property
    def last_notification(self) -> Notification | None:
        """Return the last notification."""
        if self.notifications:
            return self.notifications[-1]
        return None

    @property
    def motions(self) -> list[Notification]:
        """Return all the motion notifications."""
        return [
            notif
            for notif in self._notifications
            if notif.sub_type == NotificationSubType.MOTION_VIDEO
        ]

    @property
    def last_motion(self) -> Notification | None:
        """Return the last motion notification."""
        if self.motions:
            return self.motions[-1]
        return None

    @property
    def rings(self) -> list[Notification]:
        """Return all the rings notifications."""
        return [
            notif
            for notif in self._notifications
            if notif.sub_type == NotificationSubType.RING
        ]

    @property
    def last_ring(self) -> Notification | None:
        """Return the last ring notification."""
        if self.rings:
            return self.rings[-1]
        return None
