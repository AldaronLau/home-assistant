"""Support for deCONZ covers."""

from pydeconz.light import Cover

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    DEVICE_CLASS_DAMPER,
    DEVICE_CLASS_SHADE,
    DOMAIN,
    SUPPORT_CLOSE,
    SUPPORT_CLOSE_TILT,
    SUPPORT_OPEN,
    SUPPORT_OPEN_TILT,
    SUPPORT_SET_POSITION,
    SUPPORT_SET_TILT_POSITION,
    SUPPORT_STOP,
    SUPPORT_STOP_TILT,
    CoverEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .deconz_device import DeconzDevice
from .gateway import get_gateway_from_config_entry

DEVICE_CLASS = {
    "Level controllable output": DEVICE_CLASS_DAMPER,
    "Window covering controller": DEVICE_CLASS_SHADE,
    "Window covering device": DEVICE_CLASS_SHADE,
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up covers for deCONZ component."""
    gateway = get_gateway_from_config_entry(hass, config_entry)
    gateway.entities[DOMAIN] = set()

    @callback
    def async_add_cover(lights=gateway.api.lights.values()):
        """Add cover from deCONZ."""
        entities = []

        for light in lights:
            if (
                isinstance(light, Cover)
                and light.unique_id not in gateway.entities[DOMAIN]
            ):
                entities.append(DeconzCover(light, gateway))

        if entities:
            async_add_entities(entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            gateway.signal_new_light,
            async_add_cover,
        )
    )

    async_add_cover()


class DeconzCover(DeconzDevice, CoverEntity):
    """Representation of a deCONZ cover."""

    TYPE = DOMAIN

    def __init__(self, device, gateway):
        """Set up cover device."""
        super().__init__(device, gateway)

        self._attr_supported_features = SUPPORT_OPEN
        self._attr_supported_features |= SUPPORT_CLOSE
        self._attr_supported_features |= SUPPORT_STOP
        self._attr_supported_features |= SUPPORT_SET_POSITION

        if self._device.tilt is not None:
            self._attr_supported_features |= SUPPORT_OPEN_TILT
            self._attr_supported_features |= SUPPORT_CLOSE_TILT
            self._attr_supported_features |= SUPPORT_STOP_TILT
            self._attr_supported_features |= SUPPORT_SET_TILT_POSITION

        self._attr_device_class = DEVICE_CLASS.get(self._device.type)

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return 100 - self._device.lift

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return not self._device.is_open

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = 100 - kwargs[ATTR_POSITION]
        await self._device.set_position(lift=position)

    async def async_open_cover(self, **kwargs):
        """Open cover."""
        await self._device.open()

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        await self._device.close()

    async def async_stop_cover(self, **kwargs):
        """Stop cover."""
        await self._device.stop()

    @property
    def current_cover_tilt_position(self):
        """Return the current tilt position of the cover."""
        if self._device.tilt is not None:
            return 100 - self._device.tilt
        return None

    async def async_set_cover_tilt_position(self, **kwargs):
        """Tilt the cover to a specific position."""
        position = 100 - kwargs[ATTR_TILT_POSITION]
        await self._device.set_position(tilt=position)

    async def async_open_cover_tilt(self, **kwargs):
        """Open cover tilt."""
        await self._device.set_position(tilt=0)

    async def async_close_cover_tilt(self, **kwargs):
        """Close cover tilt."""
        await self._device.set_position(tilt=100)

    async def async_stop_cover_tilt(self, **kwargs):
        """Stop cover tilt."""
        await self._device.stop()
