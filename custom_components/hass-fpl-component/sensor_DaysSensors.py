import datetime
from homeassistant.components.sensor import SensorStateClass
from .fplEntity import FplDayEntity

class ServiceDaysSensor(FplDayEntity):
  """Service days sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Service Days")

  _attr_state_class = SensorStateClass.MEASUREMENT

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    service_days = self.getData("service_days")

    if service_days is not None:
      self._attr_native_value = service_days

    return self._attr_native_value

class AsOfDaysSensor(FplDayEntity):
  """As of days sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "As Of Days")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    as_of_days = self.getData("as_of_days")

    if as_of_days is not None:
      self._attr_native_value = as_of_days

    return self._attr_native_value

class RemainingDaysSensor(FplDayEntity):
  """Remaining days sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Remaining Days")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    remaining_days = self.getData("remaining_days")

    if remaining_days is not None:
      self._attr_native_value = remaining_days

    return self._attr_native_value
