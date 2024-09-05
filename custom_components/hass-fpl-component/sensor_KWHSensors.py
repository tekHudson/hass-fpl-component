"""Energy sensors."""
from homeassistant.components.sensor import SensorStateClass
from .fplEntity import FplEnergyEntity

class ProjectedKWHSensor(FplEnergyEntity):
  """Projected KWH sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Projected KWH")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    projected_kwh = self.getData("projected_kwh")

    if projected_kwh is not None:
      self._attr_native_value = projected_kwh

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL
    return attributes

class DailyAverageKWHSensor(FplEnergyEntity):
  """Daily Average KWH sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Daily Average KWH")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    daily_average_kwh = self.getData("daily_average_kwh")

    if daily_average_kwh is not None:
      self._attr_native_value = daily_average_kwh

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL
    return attributes

class BillToDateKWHSensor(FplEnergyEntity):
  """Bill To Date KWH sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Bill To Date KWH")

  _attr_state_class = SensorStateClass.TOTAL_INCREASING

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    bill_to_date_kwh = self.getData("bill_to_date_kwh")

    if bill_to_date_kwh is not None:
      self._attr_native_value = bill_to_date_kwh

    # print(self.state_class)

    return self._attr_native_value

class NetReceivedKWHSensor(FplEnergyEntity):
  """Received Meter Reading KWH sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Net Received KWH")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    recieved_meter_reading = self.getData("recieved_meter_reading")

    if recieved_meter_reading is not None:
      self._attr_native_value = recieved_meter_reading

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL_INCREASING
    return attributes

class NetDeliveredKWHSensor(FplEnergyEntity):
  """Delivered Meter Reading KWH sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Net Delivered KWH")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    delivered_meter_reading = self.getData("delivered_meter_reading")

    if delivered_meter_reading is not None:
      self._attr_native_value = delivered_meter_reading

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL_INCREASING
    return attributes

class DailyUsageKWHSensor(FplEnergyEntity):
  """Daily Usage Kwh Sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Daily Usage KWH")

  _attr_state_class = SensorStateClass.TOTAL_INCREASING

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    data = self.getData("daily_usage")

    if data is not None and len(data) > 0 and "kwh_usage" in data[-1]:
      self._attr_native_value = data[-1]["kwh_usage"]

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    data = self.getData("daily_usage")
    attributes = {}

    if data is not None and len(data) > 0 and "read_time" in data[-1]:
      date = data[-1]["read_time"]
      attributes["date"] = date
    return attributes

class DailyReceivedKWHSensor(FplEnergyEntity):
  """Daily received Kwh sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Daily Received KWH")

  _attr_state_class = SensorStateClass.TOTAL_INCREASING

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    data = self.getData("daily_usage")

    if data is not None and len(data) > 0 and "netReceivedKwh" in data[-1]:
      self._attr_native_value = data[-1]["netReceivedKwh"]

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    data = self.getData("daily_usage")
    attributes = {}

    if data is not None and len(data) > 0 and "read_time" in data[-1]:
      date = data[-1]["read_time"]
      attributes["date"] = date
    return attributes

class DailyDeliveredKWHSensor(FplEnergyEntity):
  """Daily delivered Kwh sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Daily Delivered KWH")

  _attr_state_class = SensorStateClass.TOTAL_INCREASING

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    data = self.getData("daily_usage")

    if data is not None and len(data) > 0 and "net_delivered_kwh" in data[-1]:
      self._attr_native_value = data[-1]["net_delivered_kwh"]

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    data = self.getData("daily_usage")
    attributes = {}
    if data is not None and len(data) > 0 and "read_time" in data[-1]:
      date = data[-1]["read_time"]
      attributes["date"] = date
    return attributes
