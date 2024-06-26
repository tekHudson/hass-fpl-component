"""Test Sensors."""
from datetime import datetime
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import STATE_UNKNOWN
from .fplEntity import FplEnergyEntity


class TestSensor(FplEnergyEntity):
    """Daily Usage Kwh Sensor."""

    def __init__(self, coordinator, config, account):
        """Initialize the class."""
        super().__init__(coordinator, config, account, "Test Sensor")

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        data = self.getData("daily_usage")

        if data is not None and len(data) > 0 and "usage" in data[-1]:
            return data[-1]["usage"]

        return STATE_UNKNOWN

    @property
    def last_reset(self) -> datetime | None:
        """Return the time when the sensor was last reset, if any."""
        last_reset = None
        data = self.getData("daily_usage")
        if len(data) > 0 and "readTime" in data[-1]:
            date = data[-1]["readTime"]
            last_reset = datetime.combine(date, datetime.min.time())
            # print("setting last reset {last_reset}")
        return last_reset

    def customAttributes(self):
        """Return the state attributes."""
        # print("setting custom attributes")
        data = self.getData("daily_usage")
        date = data[-1]["readTime"]

        attributes = {}
        attributes["date"] = date
        # last_reset = date - timedelta(days=1)
        # attributes["last_reset"] = last_reset
        return attributes
