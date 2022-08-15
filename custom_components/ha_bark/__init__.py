from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, DATA_BARK

PLATFORMS = [Platform.NOTIFY]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data[DATA_BARK] = config
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    # set up notify platform, no entry support for notify component yet,
    # have to use discovery to load platform.
    config = hass.data[DATA_BARK]
    hass.async_create_task(
        discovery.async_load_platform(
            hass, Platform.NOTIFY, DOMAIN, entry.data, config
        )
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    
    return unload_ok
