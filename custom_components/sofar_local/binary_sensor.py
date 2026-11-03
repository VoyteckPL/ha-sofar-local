from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from homeassistant.helpers.entity import (
    DeviceInfo,
)

from .const import (
    DOMAIN,
    CONF_LOGGER_SERIAL,
)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    coordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    async_add_entities(
        [
            SofarOnline(
                coordinator,
                entry,
            )
        ]
    )


class SofarOnline(
    CoordinatorEntity,
    BinarySensorEntity,
):

    _attr_has_entity_name = True
    _attr_name = "Online"

    _attr_device_class = (
        BinarySensorDeviceClass.CONNECTIVITY
    )

    def __init__(
        self,
        coordinator,
        entry,
    ):

        super().__init__(
            coordinator
        )

        serial = entry.data[
            CONF_LOGGER_SERIAL
        ]

        self._attr_unique_id = (
            f"{serial}_online"
        )

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    str(serial),
                )
            },
            name="Fotowoltaika",
            manufacturer="SOFAR Solar",
            model="4.4KTLX-G3",
        )

    @property
    def is_on(self):
        # Prawdziwy stan komunikacji z falownikiem.
        # Coordinator ustawia is_online=False po dwóch
        # pełnych nieudanych cyklach odczytu.
        return self.coordinator.is_online
