"""Fenotek client module."""

import logging
from typing import Any, cast

import aiohttp

from .api_reponse import (
    LoginResponse,
    PingResponse,
    VisiophoneHomeResponse,
    VisiophoneResponse,
    VisiophonesResponse,
)
from .consts import (
    FENOTEK_DRYCONTACT_ACTIVATE,
    FENOTEK_LOGIN,
    FENOTEK_PING,
    FENOTEK_URL,
    FENOTEK_VISIONPHONE,
    FENOTEK_VISIONPHONE_HOME,
    FENOTEK_VISIONPHONES,
)


class FenotekClient:
    """Fenotek client class."""

    def __init__(
        self,
        username: str,
        password: str,
        timezone: str,
        websession: aiohttp.ClientSession | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Fenotek client class constructor."""
        self._username: str = username
        self._password: str = password
        self._timezone: str = timezone
        self._websession: aiohttp.ClientSession = websession or aiohttp.ClientSession()
        self._token: str | None = None
        self._logger: logging.Logger = logger or logging.getLogger("fenotek-client")

    @property
    def headers(self) -> dict[str, str]:
        """Get headers needed for HTTP queries."""
        headers = {}
        headers["content-type"] = "application/json"
        if self._token is not None:
            headers["x-access-tokens"] = self._token
        return headers

    async def _http_request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
        status_code: int = 200,
        need_loggedin: bool = False,
    ) -> dict[str, Any]:
        """Make a HTTP query."""
        if need_loggedin and self._token is None:
            await self.login()

        url = FENOTEK_URL + path
        method = method.lower()
        if method not in ("post", "get"):
            raise

        try:
            res: aiohttp.ClientResponse = await getattr(self._websession, method)(
                url, headers=self.headers, json=data
            )
        except Exception as exp:
            raise RuntimeError from exp
        if res.status != status_code:
            raise
        try:
            json_res: dict[str, Any] = await res.json()
        except Exception as exp:
            raise RuntimeError from exp
        return json_res

    async def login(self) -> bool:
        """Login to the API."""
        data = {
            "email": self._username,
            "password": self._password,
            "device": {
                "pushType": "",
                "timeZone": self._timezone,
                "type": "hass",
                "duid": "",
                "bypassDnd": True,
                "tokenId": "",
            },
        }
        json_res = cast(
            LoginResponse,
            await self._http_request(method="post", path=FENOTEK_LOGIN, data=data),
        )
        if "token" not in json_res:
            self._logger.error(json_res["error"])
            return False
        self._token = json_res["token"]
        return True

    async def get_doorbells(self) -> VisiophonesResponse:
        """Get list of doorbell IDs."""
        json_res = cast(
            VisiophonesResponse, await self._http_request("get", FENOTEK_VISIONPHONES)
        )
        return json_res

    async def get_doorbell(self, doorbell_id: str) -> VisiophoneResponse:
        """Get doorbell data."""
        json_res = cast(
            VisiophoneResponse,
            await self._http_request("get", FENOTEK_VISIONPHONE.format(doorbell_id)),
        )
        return json_res

    async def ping(self, doorbell_id: str) -> bool:
        """Ping doorbell."""
        try:
            json_res = cast(
                PingResponse,
                await self._http_request(
                    method="post", path=FENOTEK_PING.format(doorbell_id), data={}
                ),
            )
        except Exception:
            return False
        return bool(json_res.get("success", False))

    async def home(self, doorbell_id: str) -> VisiophoneHomeResponse:
        """Get doorbell home data."""
        json_res = cast(
            VisiophoneHomeResponse,
            await self._http_request(
                "get", path=FENOTEK_VISIONPHONE_HOME.format(doorbell_id)
            ),
        )
        json_res["lastNotification"]["detail"]["videoUrl"] = ""
        if json_res.get("lastNotification", {}).get("detail", {}).get("type") == 5:
            # TODO: detail what id notification type 5
            # maybe when the doorbell ring ?
            video_data_url = (
                json_res.get("lastNotification", {}).get("detail", {}).get("url")
            )
            assert isinstance(video_data_url, str)
            json_res2 = await self._http_request(method="get", path=video_data_url)
            # print(json_res2)
            json_res["lastNotification"]["detail"]["videoUrl"] = json_res2["data"][
                "url"
            ]
            json_res["lastNotification"]["detail"]["url"] = json_res.get("mediaUrl", "")
        return json_res

    async def trigger_drycontact(self, doorbell_id: str, drycontact_id: str) -> bool:
        """Activate a dry contact."""
        data = {"securityCode": ""}
        json_res = await self._http_request(
            method="post",
            path=FENOTEK_DRYCONTACT_ACTIVATE.format(doorbell_id, drycontact_id),
            data=data,
        )

        if json_res.get("error"):
            self._logger.error(
                "%s - Activate dry contact - %s",
                json_res.get("error", "Error"),
                json_res.get("schemaError", {}).get("message", "Unknown"),
            )
            return False
        return bool(json_res.get("success", False))

    async def fetch_camera_image(self, url: str) -> bytes:
        """Fetch camera image raw data."""
        res = await self._websession.get(url)
        content = await res.read()
        return content
