"""Support for iOS push notifications."""
from http import HTTPStatus
import logging

import requests

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    BaseNotificationService
)
from homeassistant.const import CONF_NAME, CONF_URL
from .const import ATTR_AUTO_COPY, ATTR_BADGE, ATTR_COPY, ATTR_GROUP, ATTR_ICON, ATTR_SOUND, ATTR_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def get_service(hass, config, discovery_info=None):
    return BarkNotificationService(discovery_info[CONF_NAME], discovery_info[CONF_URL])


class BarkNotificationService(BaseNotificationService):
    """Implement the notification service for iOS."""

    def __init__(self, name, url):
        """Initialize the service."""
        self._url = url

    def send_message(self, message="", **kwargs):
        url = self._url

        if (
            (title := kwargs.get(ATTR_TITLE)) is not None
            and title != ATTR_TITLE_DEFAULT
        ):
            url += "/" + title

        url += "/" + message

        params = {}
        if (data := kwargs.get(ATTR_DATA)) is not None:
            if (copy := data.get(ATTR_COPY)) is not None:
                params["copy"] = copy
                if data.get(ATTR_AUTO_COPY):
                    params["autoCopy"] = 1
            if (badge := data.get(ATTR_BADGE)) is not None:
                params["badge"] = badge
            if (purl := data.get(ATTR_URL)) is not None:
                params["url"] = purl
            if (group := data.get(ATTR_GROUP)) is not None:
                params["group"] = group
            if (icon := data.get(ATTR_ICON)) is not None:
                params["icon"] = icon
            if (sound := data.get(ATTR_SOUND)) is not None:
                params["sound"] = sound

        requests.get(url, params, timeout=10)

