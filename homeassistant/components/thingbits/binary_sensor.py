"""ThingBits Binary Sensors."""

import thingbits_ha

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)

SIGNAL_UPDATE_ENTITY = "thingbits_{}"


def send_event(device_id, hass, data):
    """Send event to HomeAssistant from thingbits_ha (callback)."""

    # if entity != None:
    #    entity._update_callback()

    async_dispatcher_send(hass, SIGNAL_UPDATE_ENTITY.format(device_id))

    # print("Test Event")
    # event_data = {
    #    "device_id": device_id,
    #    "type": data,
    # }
    # hass.bus.async_fire("thingbits_event", event_data)


async def async_setup_entry(hass, config, async_add_entities):
    """Set up the ThingBits binary sensors."""
    # data = hass.data[DOMAIN][config.entry_id]
    devices = await hass.async_add_executor_job(thingbits_ha.devices)
    entities = []
    for device in devices:
        if device["type"] == "DUMMY":
            entities.append(DummyBinarySensor(device))
            thingbits_ha.listen(device["id"], hass, send_event)

    async_add_entities(entities)


class DummyBinarySensor(BinarySensorEntity):
    """Representation of a Dummy binary sensor."""

    def __init__(self, data):
        """Initialize the sensor."""
        self.data = data
        self._state = None
        self._remove_signal_update = None

    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        self._remove_signal_update = async_dispatcher_connect(
            self.hass,
            SIGNAL_UPDATE_ENTITY.format(self.data["id"]),
            self._update_callback,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Call when entity will be removed from hass."""
        self._remove_signal_update()

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.data["name"]

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    async def async_update(self):
        """Update sensor state."""
        print("updating")
        self._state = not self._state  # await async_fetch_state()

    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)
