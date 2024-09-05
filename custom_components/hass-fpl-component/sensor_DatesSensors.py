"""Dates sensors."""
import datetime
from homeassistant.components.sensor import SensorStateClass
from .fplEntity import FplDateEntity

class CurrentBillDateSensor(FplDateEntity):
  """Current bill date sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Current Bill Date")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    current_bill_date = self.getData("current_bill_date")

    if current_bill_date is not None:
      self._attr_native_value = datetime.date.fromisoformat(current_bill_date)

    return self._attr_native_value

class NextBillDateSensor(FplDateEntity):
  """Next bill date sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Next Bill Date")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    next_bill_date = self.getData("next_bill_date")

    if next_bill_date is not None:
      self._attr_native_value = datetime.date.fromisoformat(next_bill_date)

    return self._attr_native_value

