"""Test Sensor, no clue why."""


from .fplEntity import FplEntity
# import pprint


class TestSensor(FplEntity):
  """Test Sensor, no clue why."""

  def __init__(self, coordinator, config, account):
    """Initialize the class."""
    super().__init__(coordinator, config, account, "Test Sensor")

  @property
  def state(self):
    """Return the projected bill, no clue why."""
    # pprint.pprint(self.coordinator.data)

    return self.getData("projected_bill")

  def defineAttributes(self):
    """Return the state attributes."""
    attributes = {}
    try:
      if self.getData("budget_bill"):
        attributes["budget_bill"] = self.getData("budget_bill")
    except Exception as _:
      pass

    return attributes

  @property
  def icon(self):
    """Return mdi icon name."""
    return "mdi:currency-usd"
