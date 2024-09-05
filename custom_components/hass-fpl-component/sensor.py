"""Sensor platform for custom_components/hass-fpl-component."""

from .sensor_KWHSensors import (
  ProjectedKWHSensor,
  DailyAverageKWHSensor,
  BillToDateKWHSensor,
  NetReceivedKWHSensor,
  NetDeliveredKWHSensor,
  DailyUsageKWHSensor,
  DailyReceivedKWHSensor,
  DailyDeliveredKWHSensor,
)
from .sensor_DatesSensors import (
  CurrentBillDateSensor,
  NextBillDateSensor,
)
from .sensor_DaysSensors import (
  ServiceDaysSensor,
  AsOfDaysSensor,
  RemainingDaysSensor,
)
from .sensor_MonetarySensors import (
  BalanceSensor,
  DailyAverageSensor,
  BudgetDailyAverageSensor,
  ActualDailyAverageSensor,
  FplDailyUsageSensor,
  FplProjectedBillSensor,
  DeferedAmountSensor,
  ProjectedBudgetBillSensor,
  ProjectedActualBillSensor,
  BillToDateSensor,
)

from .sensor_MonetarySensors import BalanceSensor

from .const import CONF_ACCOUNTS, CONF_TERRITORY, DOMAIN, FPL_MAINREGION, FPL_NORTHWEST

ALL_REGIONS = [FPL_MAINREGION, FPL_NORTHWEST]
ONLY_MAINREGION = [FPL_MAINREGION]

sensors = {}


def registerSensor(sensor, regions):
  """Register all available sensors."""
  for region in regions:
    if region in sensors:
      sensors[region].append(sensor)
    else:
      sensors[region] = [sensor]


# bill sensors
registerSensor(FplProjectedBillSensor, ALL_REGIONS)
registerSensor(BillToDateSensor, ALL_REGIONS)

# budget billing
registerSensor(ProjectedBudgetBillSensor, ONLY_MAINREGION)
registerSensor(ProjectedActualBillSensor, ONLY_MAINREGION)
registerSensor(DeferedAmountSensor, ONLY_MAINREGION)


# monetary sensors
registerSensor(DailyAverageSensor, ONLY_MAINREGION)
registerSensor(BudgetDailyAverageSensor, ONLY_MAINREGION)
registerSensor(ActualDailyAverageSensor, ONLY_MAINREGION)

# date sensors
registerSensor(CurrentBillDateSensor, ALL_REGIONS)
registerSensor(NextBillDateSensor, ONLY_MAINREGION)
registerSensor(ServiceDaysSensor, ALL_REGIONS)
registerSensor(AsOfDaysSensor, ALL_REGIONS)
registerSensor(RemainingDaysSensor, ALL_REGIONS)

# KWH sensors
registerSensor(ProjectedKWHSensor, ALL_REGIONS)
registerSensor(DailyAverageKWHSensor, ONLY_MAINREGION)
registerSensor(BillToDateKWHSensor, ALL_REGIONS)
registerSensor(FplDailyUsageSensor, ONLY_MAINREGION)
registerSensor(NetReceivedKWHSensor, ONLY_MAINREGION)
registerSensor(NetDeliveredKWHSensor, ONLY_MAINREGION)
registerSensor(DailyUsageKWHSensor, ONLY_MAINREGION)
registerSensor(DailyReceivedKWHSensor, ONLY_MAINREGION)
registerSensor(DailyDeliveredKWHSensor, ONLY_MAINREGION)

# Balance sensors
registerSensor(BalanceSensor, ONLY_MAINREGION)


async def async_setup_entry(hass, entry, async_add_devices):
  """Set up sensor platform."""

  accounts = entry.data.get(CONF_ACCOUNTS)
  territory = entry.data.get(CONF_TERRITORY)

  coordinator = hass.data[DOMAIN][entry.entry_id]
  fpl_accounts = []

  for account in accounts:
    for sensor in sensors[territory]:
      fpl_accounts.append(sensor(coordinator, entry, account))

  async_add_devices(fpl_accounts)
