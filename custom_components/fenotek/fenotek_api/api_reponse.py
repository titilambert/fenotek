"""HTTP response data structures module."""

from typing import Any, NotRequired, TypedDict


# Ping
class PingResponse(TypedDict):
    """Ping query HTTP response."""

    success: bool


# Login
class LoginResponse(TypedDict):
    """Login query HTTP response."""

    token: str
    error: NotRequired[str]


# Visiophones
class VisiophonesResponse(TypedDict):
    """Visiophones query HTTP response."""

    visiophones: list[str]


# Visiophone
class DrycontactResponse(TypedDict):
    """Subdata drycontact Visiophone query HTTP response."""

    name: str
    commandId: str
    isOnHold: bool
    icon: str
    delay: int
    _id: str
    createdAt: str
    updatedAt: str


class MemberResponse(TypedDict):
    """Subdata member Visiophone query HTTP response."""

    userId: str
    isAdmin: bool
    _id: str
    createdAt: str
    updatedAt: str


class ZoneResponse(TypedDict):
    """Subdata member Visiophone query HTTP response."""

    label: str
    coords: list[list[int]]
    surface: int
    _id: str
    createdAt: str
    updatedAt: str


class AddressResponse(TypedDict):
    """Subdata address Visiophone query HTTP response."""

    country: str
    street_2: str
    zipcode: str
    city: str
    street_1: str


class VisiophoneResponse(TypedDict):
    """Visiophone query HTTP response."""

    description: str
    isInStandBy: bool
    isAntiTheftAlarmEnabled: bool
    isNotificationEnabled: bool
    isTurnedOn: bool
    suspended: bool
    isUserDetectionEnabled: bool
    ledColor: int
    minor: int
    major: int
    notificationEnd: str
    notificationStart: str
    screenName: str
    sensorRange: int
    ttsLanguage: int
    timeZone: str
    isTriggerChimeOnMovementEnabled: bool
    region: str
    position: str
    isStolen: int
    androidBuildVersion: str
    hiVersion: str
    updaterVersion: str
    lastPing: str
    connectionType: str
    disconnectionAlert: bool
    disconnectionEmailAlert: bool
    disconnectionPushAlert: bool
    dryContacts: list[DrycontactResponse]
    invitations: list[Any]
    member: list[MemberResponse]
    zones: list[ZoneResponse]
    address: AddressResponse
    contacts: list[Any]
    _id: str
    createdAt: str
    updatedAt: str


class VisiophoneHomeUserResponse(TypedDict):
    """Subdata user VisiophoneHome query HTTP response."""

    name: str
    username: str
    ignorePushFrom: list[Any]
    isAdmin: bool


class VisiophoneHomeDryContactResponse(TypedDict):
    """Subdata drycontact VisiophoneHome query HTTP response."""

    name: str
    commandId: str
    isOnHold: bool
    icon: str
    delay: int


class VisiophoneHomeNotificationDetailResponse(TypedDict):
    """Subdata notification detail VisiophoneHome query HTTP response."""

    type: int
    # 0: motion with photo
    # 6: doorbell ring
    # 8: call creation
    # 10: dry contact activation
    # 11: motion with video
    # 13: doorbell reachable
    label: NotRequired[str]
    url: NotRequired[str]
    triggeredBy: NotRequired[str]
    name: NotRequired[str]
    download: NotRequired[str]
    videoUrl: NotRequired[str]
    room: NotRequired[str]
    recorded: NotRequired[bool]
    answeredBy: NotRequired[str]


class VisiophoneHomeNotificationResponse(TypedDict):
    """Subdata notification VisiophoneHome query HTTP response."""

    vuid: str
    type: str
    # notification or missedcall or drycontact or connected
    detail: VisiophoneHomeNotificationDetailResponse
    expireAt: str
    _id: str
    createdAt: str
    updatedAt: str


class VisiophoneHomeResponse(TypedDict):
    """VisiophoneHome query HTTP response."""

    vuid: str
    users: list[VisiophoneHomeUserResponse]
    dryContacts: list[VisiophoneHomeDryContactResponse]
    lastNotification: VisiophoneHomeNotificationResponse
    mediaUrl: str


class SchemaError(TypedDict):
    """Subdata error Drycontact activate query HTTP response."""

    message: str


class DrycontactActivateResponse(TypedDict):
    """Drycontact activate query HTTP response."""

    error: str
    schemaError: SchemaError
    success: bool


# Visiophone Notifications
class VisiophonesNotificationsResponse(TypedDict):
    """Doorbell notifications query HTTP response."""

    page: int
    pages: int
    notifications: list[VisiophoneHomeNotificationResponse]
