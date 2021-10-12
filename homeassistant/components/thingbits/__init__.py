"""The ThingBits integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# For your initial PR, limit it to 1 platform.
PLATFORMS = ["sensor", "binary_sensor"]


class ThingBits:
    """The ThingBits class."""

    # Binary Sensors
    BINARY_SENSOR_TYPES = [
        "DUMMY",
        "Beacon",
        "Button",
        "Toggle",
        "Tilt",
        "Shake",
        "Motion",
        "Knock",
        "Sound",
        "Reed",
        "Leak",
    ]

    # Sensors
    SENSOR_TYPES = ["T,RH", "Light", "Temp"]

    def __init__(self):
        """Init ThingBits."""
        pass


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ThingBits from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = ThingBits()

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
