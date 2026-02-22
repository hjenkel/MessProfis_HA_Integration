"""Sensor platform for MessProfis Mieterportal."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    METRIC_COLD_WATER,
    METRIC_HEATING,
    METRIC_HOT_WATER_ENERGY,
    METRIC_HOT_WATER_VOLUME,
)
from .coordinator import MessProfisDataUpdateCoordinator
from .models import ApartmentReading, MonthlyValue


@dataclass(frozen=True, kw_only=True)
class MessProfisSensorDescription(SensorEntityDescription):
    """MessProfis sensor descriptor."""

    metric_key: str


SENSOR_DESCRIPTIONS: tuple[MessProfisSensorDescription, ...] = (
    MessProfisSensorDescription(
        key=METRIC_HEATING,
        metric_key=METRIC_HEATING,
        name="Heizung aktuell",
        icon="mdi:fire",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MessProfisSensorDescription(
        key=METRIC_COLD_WATER,
        metric_key=METRIC_COLD_WATER,
        name="Kaltwasser aktuell",
        icon="mdi:water",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MessProfisSensorDescription(
        key=METRIC_HOT_WATER_ENERGY,
        metric_key=METRIC_HOT_WATER_ENERGY,
        name="Warmwasser aktuell",
        icon="mdi:water-thermometer",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MessProfisSensorDescription(
        key=METRIC_HOT_WATER_VOLUME,
        metric_key=METRIC_HOT_WATER_VOLUME,
        name="Warmwasser aktuell (m3)",
        icon="mdi:water-thermometer",
        native_unit_of_measurement="m³",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up MessProfis sensors from config entry."""
    coordinator: MessProfisDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MessProfisSensor] = []
    for apartment in coordinator.data:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(MessProfisSensor(coordinator, apartment, description))

    async_add_entities(entities)


class MessProfisSensor(
    CoordinatorEntity[MessProfisDataUpdateCoordinator], SensorEntity
):
    """Representation of one MessProfis metric sensor."""

    entity_description: MessProfisSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MessProfisDataUpdateCoordinator,
        apartment: ApartmentReading,
        description: MessProfisSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._apartment_key = apartment.apartment_key
        self._attr_unique_id = (
            f"{DOMAIN}_{self._apartment_key}_{self.entity_description.metric_key}"
        )

        apartment_name = " ".join(
            part.strip() for part in [apartment.title1, apartment.title2] if part and part.strip()
        ).strip()
        if not apartment_name:
            apartment_name = apartment.apartment_key

        self._attr_device_info = {
            "identifiers": {(DOMAIN, apartment.apartment_key)},
            "name": f"MessProfis {apartment_name}",
            "manufacturer": "Mess-Profis",
            "model": "Mieterportal",
        }
        self._attr_name = f"{apartment_name} {self.entity_description.name}"

    def _current_apartment(self) -> ApartmentReading | None:
        for apartment in self.coordinator.data:
            if apartment.apartment_key == self._apartment_key:
                return apartment
        return None

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        apartment = self._current_apartment()
        if apartment is None:
            return False
        return apartment.values.get(self.entity_description.metric_key) is not None

    @property
    def native_value(self) -> float | None:
        """Return the latest monthly value."""
        apartment = self._current_apartment()
        if apartment is None:
            return None
        value = apartment.values.get(self.entity_description.metric_key)
        return None if value is None else value.wert

    @property
    def extra_state_attributes(self) -> dict[str, str | bool | float | None]:
        """Return sensor metadata as attributes."""
        apartment = self._current_apartment()
        if apartment is None:
            return {}

        metric_key = self.entity_description.metric_key
        value: MonthlyValue | None = apartment.values.get(metric_key)
        return {
            "title1": apartment.title1,
            "title2": apartment.title2,
            "status": apartment.status,
            "last_month_date": None if value is None else value.datum,
            "estimated": None if value is None else value.estimated,
            "jahreswert": apartment.jahreswerte.get(metric_key),
        }
