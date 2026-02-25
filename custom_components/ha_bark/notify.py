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
from homeassistant.helpers.aiohttp_client  import async_get_clientsession
from .const import ATTR_AUTO_COPY, ATTR_BADGE, ATTR_CALL, ATTR_COPY, ATTR_GROUP, ATTR_ICON, ATTR_IMAGE, ATTR_IS_ARCHIVE, ATTR_LEVEL, ATTR_SOUND, ATTR_URL, ATTR_VOLUME, DATA_BARK

_LOGGER = logging.getLogger(__name__)


async def async_get_service(hass, config, discovery_info=None):
    return BarkNotificationService(hass)


class BarkNotificationService(BaseNotificationService):

    def __init__(self, hass):
        """Initialize the service."""
        self.hass = hass

    @property
    def targets(self):
        data = self.hass.data.get(DATA_BARK, {})
        return {name: name for name in data.keys()}

    async def async_send_message(self, message="", **kwargs):
        data_store = self.hass.data.get(DATA_BARK, {})
        if not data_store:
            _LOGGER.warning("Bark data not initialized")
            return False
        targets = kwargs.get(ATTR_TARGET)
        if not targets:
            targets = list(data_store.keys())
        if isinstance(targets, str):
            targets = [targets]

        session = async_get_clientsession(self.hass)

        for name in targets:
            config = data_store.get(name)
            if config is None:
                _LOGGER.warning("Target %s not found", name)
                continue

            params = {
                "body": message,
                "device_key": config[CONF_TOKEN],
            }

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
                if (call := data.get(ATTR_CALL)) is not None:
                    params["call"] = call
                if (is_archive := data.get(ATTR_IS_ARCHIVE)) is not None:
                    params["isArchive"] = is_archive
                if (level := data.get(ATTR_LEVEL)) is not None:
                    params["level"] = level
                    if (volume := data.get(ATTR_VOLUME)) is not None:
                        params["volume"] = volume
                if (image := data.get(ATTR_IMAGE)) is not None:
                    params["image"] = image

            try:
                async with session.post(
                    url=f"{config[CONF_HOST]}/push",
                    json=params,
                ) as resp:
                    resp.raise_for_status()
                    if resp.status != 200:
                        _LOGGER.warning(
                            "Bark HTTP error %s for %s",
                            resp.status,
                            name,
                        )
                        success = False
                        continue

                    result = await resp.json()
                    if result.get("code") != 200:
                        _LOGGER.warning("Bark API error: %s", result)
                    else:
                        _LOGGER.debug("Bark success: %s", result)
            except Exception as e:
                _LOGGER.error("Bark request failed: %s", e)
                success = False

        return success
