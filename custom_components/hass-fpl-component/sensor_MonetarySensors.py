"""Money sensors."""
from .fplEntity import FplMoneyEntity

class BalanceSensor(FplMoneyEntity):
  """Balance sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Balance Due")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    data = self.getData("balance_data")

    self._attr_native_value = 0

    if data is not None and len(data) > 0 and "amount" in data[0]:
      self._attr_native_value = data[0]["amount"]

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    data = self.getData("balance_data")

    if data is not None and len(data) > 0:
      if "details" in data[0]:
        attributes["details"] = data[0]["details"]
      if "dueDate" in data[0]:
        attributes["dueDate"] = data[0]["dueDate"]

    return attributes

class DailyAverageSensor(FplMoneyEntity):
  """Average daily sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Daily Average")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    daily_avg = self.getData("daily_avg")

    if daily_avg is not None:
      self._attr_native_value = daily_avg

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL
    return attributes

class BudgetDailyAverageSensor(FplMoneyEntity):
  """Budget daily average sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Budget Daily Average")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    budget_billing_daily_avg = self.getData("budget_billing_daily_avg")

    if budget_billing_daily_avg is not None:
      self._attr_native_value = budget_billing_daily_avg

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL
    return attributes

class ActualDailyAverageSensor(FplMoneyEntity):
  """Actual daily average sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Actual Daily Average")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    daily_avg = self.getData("daily_avg")

    if daily_avg is not None:
      self._attr_native_value = daily_avg

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL
    return attributes

class FplDailyUsageSensor(FplMoneyEntity):
  """Daily Billing Charged Sensor."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Daily Usage")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    data = self.getData("daily_usage")

    if data is not None and len(data) > 0 and "billing_charged" in data[-1]:
      self._attr_native_value = data[-1]["billing_charged"]

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    data = self.getData("daily_usage")
    attributes = {}
    # attributes["state_class"] = SensorStateClass.TOTAL_INCREASING
    if data is not None and len(data) > 0 and "read_time" in data[-1]:
      attributes["date"] = data[-1]["read_time"]

    return attributes

class FplProjectedBillSensor(FplMoneyEntity):
  """Projected bill sensor."""

  # _attr_state_class = SensorStateClass.TOTAL

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Projected Bill")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    budget = self.getData("budget_bill")
    budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

    projected_bill = self.getData("projected_bill")

    if budget and budget_billing_projected_bill is not None:
      self._attr_native_value = self.getData("budget_billing_projected_bill")
    else:
      if projected_bill is not None:
        self._attr_native_value = projected_bill

    return self._attr_native_value

  def customAttributes(self):
    """Return the state attributes."""
    attributes = {}
    attributes["budget_bill"] = self.getData("budget_bill")
    return attributes

class DeferedAmountSensor(FplMoneyEntity):
  """Defered amount sensor."""

  # _attr_state_class = SensorStateClass.TOTAL

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Defered Amount")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    budget_bill = self.getData("budget_bill")
    defered_amount = self.getData("defered_amount")

    if budget_bill and defered_amount is not None:
      self._attr_native_value = defered_amount

    return self._attr_native_value

class ProjectedBudgetBillSensor(FplMoneyEntity):
  """Projected budget bill sensor."""

  # _attr_state_class = SensorStateClass.TOTAL

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Projected Budget Bill")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    budget_billing_projected_bill = self.getData("budget_billing_projected_bill")

    if budget_billing_projected_bill is not None:
      self._attr_native_value = budget_billing_projected_bill

    return self._attr_native_value

class ProjectedActualBillSensor(FplMoneyEntity):
  """Projeted actual bill sensor."""

  # _attr_state_class = SensorStateClass.TOTAL

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Projected Actual Bill")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    projected_bill = self.getData("projected_bill")

    if projected_bill is not None:
      self._attr_native_value = projected_bill

    return self._attr_native_value

class BillToDateSensor(FplMoneyEntity):
  """Projeted actual bill sensor."""

  # _attr_state_class = SensorStateClass.TOTAL

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Bill To Date")

  @property
  def native_value(self):
    """Return the value reported by the sensor."""
    budget_bill = self.getData("budget_bill")
    budget_billing_bill_to_date = self.getData("budget_billing_bill_to_date")
    bill_to_date = self.getData("bill_to_date")

    if budget_bill:
      self._attr_native_value = budget_billing_bill_to_date
    else:
      self._attr_native_value = bill_to_date

    return self._attr_native_value
