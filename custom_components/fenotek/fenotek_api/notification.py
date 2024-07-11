"""Notification module."""

import json
from datetime import datetime
from enum import Enum

from .api_reponse import (
    VisiophoneHomeNotificationDetailResponse,
    VisiophoneHomeNotificationResponse,
)
from .client import FenotekClient


class NotificationType(Enum):
    """List of notification types."""

    DRY_CONTACT = "drycontact"
    NOTIFICATION = "notification"
    CALL = "call"
    MISSED_CALL = "missedcall"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class NotificationSubType(Enum):
    """List of notification sub types."""

    UNKNOWN = -1
    MOTION_IMAGE = 0
    ANSWERED_CALL = 3
    RING = 6
    SHAKED = 7  # TODO: validate that
    MISSED_CALL = 8
    ACTIVATION = 10
    MOTION_VIDEO = 11
    DOORBELL_UNREACHABLE = 12
    DOORBELL_REACHABLE = 13


class Notification:
    """Notification class."""

    def __init__(
        self,
        fenotek_client: FenotekClient,
        id_: str,
        type_: str,
        created_at: datetime,
        details: VisiophoneHomeNotificationDetailResponse,
    ):
        """Notification class construction."""
        self._fenotek_client: FenotekClient = fenotek_client
        self._id: str = id_
        self._type: str = type_
        self._created_at: datetime = created_at
        self._details: VisiophoneHomeNotificationDetailResponse = details
        self._video_url: str = ""

    @property
    def id_(self) -> str:
        """Return notification ID."""
        return self._id

    @property
    def type_(self) -> NotificationType:
        """Return notification type."""
        return NotificationType(self._type)

    @property
    def created_at(self) -> datetime:
        """Return notification creation date."""
        return self._created_at

    @property
    def label(self) -> str:
        """Return notification label."""
        return self._details.get("label", "")

    @property
    def name(self) -> str:
        """Return the name of who triggered the notification."""
        return self._details.get("name", "")

    @property
    def sub_type(self) -> NotificationSubType:
        """Return notification sub type."""
        return NotificationSubType(self._details.get("type", -1))

    @property
    def url(self) -> str:
        """Notification data url.

        Could be:
        * a jpeg file
        * json data with link to mp4 file
        """
        return self._details.get("url", "")

    @property
    def download(self) -> str:
        """mp4 video file url."""
        return self._details.get("download", "")

    @property
    def video_url(self) -> str:
        """Return video url."""
        if self._video_url:
            return self._video_url
        return self.url

    @classmethod
    def new(
        self,
        fenotek_client: FenotekClient,
        notification_raw_data: VisiophoneHomeNotificationResponse,
    ) -> "Notification":
        """Create new notification object."""
        notif = Notification(
            fenotek_client=fenotek_client,
            id_=notification_raw_data["_id"],
            type_=notification_raw_data["type"],
            created_at=datetime.fromisoformat(notification_raw_data["createdAt"]),
            details=notification_raw_data["detail"],
        )
        return notif

    async def fetch_details_url(self) -> bytes | None:
        """Get the content of the url in the details."""
        if not self.url:
            return None
        data = await self._fenotek_client.fetch_url(self.url)
        if self.sub_type in (
            NotificationSubType.MISSED_CALL,
            NotificationSubType.ANSWERED_CALL,
        ):
            self._video_url = json.loads(data).get("data", {}).get("url", {})
        return data

    def __repr__(self) -> str:
        """Object representation."""
        return (
            f"""<Notification - {self._id} - {self.created_at}"""
            f""" - {self.type_} - {self.sub_type}>"""
        )
