from dataclasses import dataclass

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
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


@dataclass(
    frozen=True,
    kw_only=True,
)
class SofarSensorDescription(
    SensorEntityDescription
):
    pass


def _format_minutes(value):
    try:
        total = int(round(float(value)))
    except (TypeError, ValueError):
        return None

    years, remaining = divmod(total, 525600)
    days, remaining = divmod(remaining, 1440)
    hours, minutes = divmod(remaining, 60)

    parts = []
    if years:
        parts.append(f"{years} r")
    if days:
        parts.append(f"{days} d")
    if hours:
        parts.append(f"{hours} godz")
    if minutes or not parts:
        parts.append(f"{minutes} min")

    return " ".join(parts)


ZERO_WHEN_OFFLINE = {
    "current_power",
    "phase_r_current",
    "phase_s_current",
    "phase_t_current",
    "string_1_current",
    "string_1_power",
    "string_2_current",
    "string_2_power",
}

SENSORS = (

    SofarSensorDescription(
        key="current_power",
        name="Aktualna produkcja",
        native_unit_of_measurement=
            UnitOfPower.WATT,
        device_class=
            SensorDeviceClass.POWER,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="energy_today",
        name="Produkcja dzisiaj",
        native_unit_of_measurement=
            UnitOfEnergy.KILO_WATT_HOUR,
        device_class=
            SensorDeviceClass.ENERGY,
        state_class=
            SensorStateClass.TOTAL_INCREASING,
    ),

    SofarSensorDescription(
        key="energy_total",
        name="Produkcja całkowita",
        native_unit_of_measurement=
            UnitOfEnergy.KILO_WATT_HOUR,
        device_class=
            SensorDeviceClass.ENERGY,
        state_class=
            SensorStateClass.TOTAL_INCREASING,
    ),

    SofarSensorDescription(
        key="phase_r_voltage",
        name="Napięcie faza R",
        native_unit_of_measurement=
            UnitOfElectricPotential.VOLT,
        device_class=
            SensorDeviceClass.VOLTAGE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="phase_s_voltage",
        name="Napięcie faza S",
        native_unit_of_measurement=
            UnitOfElectricPotential.VOLT,
        device_class=
            SensorDeviceClass.VOLTAGE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="phase_t_voltage",
        name="Napięcie faza T",
        native_unit_of_measurement=
            UnitOfElectricPotential.VOLT,
        device_class=
            SensorDeviceClass.VOLTAGE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="phase_r_current",
        name="Natężenie faza R",
        native_unit_of_measurement=
            UnitOfElectricCurrent.AMPERE,
        device_class=
            SensorDeviceClass.CURRENT,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="phase_s_current",
        name="Natężenie faza S",
        native_unit_of_measurement=
            UnitOfElectricCurrent.AMPERE,
        device_class=
            SensorDeviceClass.CURRENT,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="phase_t_current",
        name="Natężenie faza T",
        native_unit_of_measurement=
            UnitOfElectricCurrent.AMPERE,
        device_class=
            SensorDeviceClass.CURRENT,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="string_1_voltage",
        name="Napięcie string 1",
        native_unit_of_measurement=
            UnitOfElectricPotential.VOLT,
        device_class=
            SensorDeviceClass.VOLTAGE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="string_1_current",
        name="Natężenie string 1",
        native_unit_of_measurement=
            UnitOfElectricCurrent.AMPERE,
        device_class=
            SensorDeviceClass.CURRENT,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="string_1_power",
        name="Moc string 1",
        native_unit_of_measurement=
            UnitOfPower.WATT,
        device_class=
            SensorDeviceClass.POWER,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="string_2_voltage",
        name="Napięcie string 2",
        native_unit_of_measurement=
            UnitOfElectricPotential.VOLT,
        device_class=
            SensorDeviceClass.VOLTAGE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="string_2_current",
        name="Natężenie string 2",
        native_unit_of_measurement=
            UnitOfElectricCurrent.AMPERE,
        device_class=
            SensorDeviceClass.CURRENT,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="string_2_power",
        name="Moc string 2",
        native_unit_of_measurement=
            UnitOfPower.WATT,
        device_class=
            SensorDeviceClass.POWER,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="ambient_temperature",
        name="Temperatura otoczenia",
        native_unit_of_measurement=
            UnitOfTemperature.CELSIUS,
        device_class=
            SensorDeviceClass.TEMPERATURE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="radiator_temperature",
        name="Temperatura radiatora",
        native_unit_of_measurement=
            UnitOfTemperature.CELSIUS,
        device_class=
            SensorDeviceClass.TEMPERATURE,
        state_class=
            SensorStateClass.MEASUREMENT,
    ),

    SofarSensorDescription(
        key="generation_time_today",
        name="Czas generacji dzisiaj",
    ),

    SofarSensorDescription(
        key="total_generation_time",
        name="Całkowity czas generowania",
    ),

    SofarSensorDescription(
        key="total_inverter_work_time",
        name="Całkowity czas pracy falownika",
    ),
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
        SofarSensor(
            coordinator,
            entry,
            desc,
        )
        for desc in SENSORS
    )
    async_add_entities([SofarInfoSensor(entry)])


class SofarSensor(
    CoordinatorEntity,
    RestoreSensor,
):

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry,
        description,
    ):

        super().__init__(
            coordinator
        )

        self.entity_description = (
            description
        )

        # Ostatnia znana wartość sprzed restartu HA (używana, dopóki
        # falownik nie odpowie, np. po restarcie w nocy).
        self._restored = None

        serial = entry.data[
            CONF_LOGGER_SERIAL
        ]

        self._attr_unique_id = (
            f"{serial}_"
            f"{description.key}"
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

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        last = await self.async_get_last_sensor_data()
        if last is not None:
            self._restored = last.native_value

    @property
    def native_value(self):
        key = self.entity_description.key

        # Gdy falownik śpi / jest offline:
        # moc i prądy mają fizycznie sens jako 0.
        if not self.coordinator.is_online and key in ZERO_WHEN_OFFLINE:
            return 0

        # Coordinator zachowuje ostatnią poprawną wartość,
        # więc pozostałe sensory nie robią dziur w historii.
        value = (self.coordinator.data or {}).get(key)

        # Brak odczytu od startu HA (np. falownik śpi): pokaż ostatnią
        # znaną wartość zamiast "nieznany".
        if value is None:
            return self._restored

        if key in (
            "generation_time_today",
            "total_generation_time",
            "total_inverter_work_time",
        ):
            return _format_minutes(value)

        return value

    @property
    def available(self):
        # Stan komunikacji pokazuje osobny binary_sensor Online.
        # Sensory pozostają dostępne również podczas nocnego uśpienia falownika.
        return True



class SofarInfoSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Dane znamionowe"
    _attr_icon = "mdi:solar-power-variant"

    def __init__(self, entry):
        serial = entry.data[CONF_LOGGER_SERIAL]
        self._attr_unique_id = f"{serial}_inverter_info"
        self._attr_native_value = "4.4KTLX-G3"
        self._attr_extra_state_attributes = {
            "producent": "SOFAR Solar",
            "model": "4.4KTLX-G3",
            "moc_znamionowa_ac": "4000 W",
            "maksymalna_moc_ac": "4400 VA",
            "maksymalne_napiecie_dc": "1100 V",
            "zakres_mppt": "140–1000 V",
            "maksymalny_prad_wejsciowy": "22.5 A / 22.5 A",
            "sieć": "3/N/PE 380/400 V",
            "maksymalny_prad_wyjsciowy": "6.7 A",
            "czestotliwosc": "50/60 Hz",
            "stopien_ochrony": "IP65",
        }
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            name="Fotowoltaika",
            manufacturer="SOFAR Solar",
            model="4.4KTLX-G3",
        )
