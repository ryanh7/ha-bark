import logging
import requests

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    BaseNotificationService
)
from homeassistant.const import CONF_HOST, CONF_TOKEN
from .const import ATTR_AUTO_COPY, ATTR_BADGE, ATTR_COPY, ATTR_GROUP, ATTR_ICON, ATTR_SOUND, ATTR_URL, DATA_BARK

_LOGGER = logging.getLogger(__name__)


def get_service(hass, config, discovery_info=None):
    return BarkNotificationService(hass)


class BarkNotificationService(BaseNotificationService):

    def __init__(self, hass):
        """Initialize the service."""
        self.hass = hass

    @property
    def targets(self):
        """Return a dictionary of registered targets."""
        targets = {}
        for name in self.hass.data[DATA_BARK].keys():
            targets[name] = name
        return targets

    def send_message(self, message="", **kwargs):
        if not (targets := kwargs.get(ATTR_TARGET)):
            targets = self.hass.data[DATA_BARK].keys()

        for name in targets:
            if (config := self.hass.data[DATA_BARK].get(name)) is None:
                continue

            params = {}
            params["body"] = message
            params["device_key"] = config[CONF_TOKEN]

            if (
                (title := kwargs.get(ATTR_TITLE)) is not None
                and title != ATTR_TITLE_DEFAULT
            ):
                params["title"] = title

            if (data := kwargs.get(ATTR_DATA)) is not None:
                if (copy := data.get(ATTR_COPY)) is not None:
                    params["copy"] = copy
                    if data.get(ATTR_AUTO_COPY):
                        params["automaticallyCopy"] = 1
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

            requests.post(
                url=config[CONF_HOST] + "/push",
                json=params
            )
