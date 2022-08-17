from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_NAME, CONF_URL, CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import notify as hass_notify
from .const import DOMAIN, DATA_BARK

PLATFORMS = [Platform.NOTIFY]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DATA_BARK, {})
    hass.async_create_task(
        discovery.async_load_platform(
            hass, Platform.NOTIFY, DOMAIN, {CONF_NAME: "bark"}, config
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config = entry.data
    hass.data[DATA_BARK][config[CONF_NAME]] = config
    await hass_notify.async_reload(hass, DOMAIN)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    config = entry.data
    hass.data[DATA_BARK].pop(config[CONF_NAME])
    await hass_notify.async_reload(hass, DOMAIN)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle an options update."""
    config = entry.data
    hass.data[DATA_BARK][config[CONF_NAME]] = config
    await hass_notify.async_reload(hass, DOMAIN)
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    if config_entry.version == 1:
        data = {**config_entry.data}
        url = data[CONF_URL]
        index = url.rindex("/")
        data[CONF_HOST] = url[:index]
        data[CONF_TOKEN] = url[index + 1:]
        data.pop(CONF_URL)
        config_entry.version = 2
        hass.config_entries.async_update_entry(
            config_entry,
            data=data,
        )

    return True
