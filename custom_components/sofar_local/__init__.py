from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SofarCoordinator


PLATFORMS = [
    "sensor",
    "binary_sensor",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):

    # Utrzymuj czytelną nazwę istniejącego wpisu integracji.
    if entry.title != "Fotowoltaika":
        hass.config_entries.async_update_entry(
            entry,
            title="Fotowoltaika",
        )

    coordinator = SofarCoordinator(
        hass,
        entry,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(
        DOMAIN,
        {}
    )[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass,
    entry,
):

    ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if ok:
        hass.data[DOMAIN].pop(
            entry.entry_id
        )

    return ok
