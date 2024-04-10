"""Average daily sensors."""
from .fplEntity import FplMoneyEntity


class DailyAverageSensor(FplMoneyEntity):
    """Average daily sensor, use budget value if available, otherwise use actual daily values."""

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
