"""FPL Main region data collection api client."""

import sys
import logging
import aiohttp
import async_timeout
from datetime import datetime, date
from dateutil.parser import parse


from .const import (
  LOGIN_RESULT_FAILURE,
  LOGIN_RESULT_INVALIDPASSWORD,
  LOGIN_RESULT_INVALIDUSER,
  LOGIN_RESULT_OK,
  TIMEOUT,
  URL_LOGIN,
  URL_BUDGET_BILLING_GRAPH,
  URL_RESOURCES_PROJECTED_BILL,
  URL_ENERGY_SERVICE,
  URL_APPLIANCE_USAGE,
  URL_BUDGET_BILLING_PREMISE_DETAILS,
  URL_RESOURCES_HEADER,
  URL_LOGOUT,
  URL_RESOURCES_ACCOUNT,
  URL_BALANCE,
)

STATUS_CATEGORY_OPEN = "OPEN"
ENROLLED = "ENROLLED"
NOTENROLLED = "NOTENROLLED"

_LOGGER = logging.getLogger(__package__)

class FplMainRegionApiClient:
  """Fpl Main Region Api Client."""

  def __init__(self, username, password, loop, session, account_data) -> None:
    """Initialize the class."""
    self.username = username
    self.password = password
    self.loop = loop
    self.session = session
    self.account_data = account_data

  async def login(self):
    """Login into fpl."""
    # login and get account information

    async with async_timeout.timeout(TIMEOUT):
      response = await self.session.get(
        URL_LOGIN,
        auth=aiohttp.BasicAuth(self.username, self.password),
      )

    if response.status == 200:
      return LOGIN_RESULT_OK

    if response.status == 401:
      response_data = await response.json()

      if response_data["messageCode"] == LOGIN_RESULT_INVALIDUSER:
        return LOGIN_RESULT_INVALIDUSER

      if response_data["messageCode"] == LOGIN_RESULT_INVALIDPASSWORD:
        return LOGIN_RESULT_INVALIDPASSWORD

    return LOGIN_RESULT_FAILURE

  async def logout(self):
    """Log out from FPL."""
    _LOGGER.info("Logging out")

    try:
      async with async_timeout.timeout(TIMEOUT):
        await self.session.get(URL_LOGOUT)
    except Exception as e:
      _LOGGER.error(e)

  async def get_open_accounts(self):
    """Get open accounts. Returns array with active account numbers."""
    result = []

    async with async_timeout.timeout(TIMEOUT):
      response = await self.session.get(URL_RESOURCES_HEADER)

    response_data = (await response.json())["data"]
    accounts = response_data["accounts"]["data"]["data"]

    for account in accounts:
      if account["statusCategory"] == STATUS_CATEGORY_OPEN:
        result.append(account["accountNumber"])

    return result

  async def update(self, account_number) -> dict:
    """Get data updates from FPL."""
    update_data = {}

    await self._get_account_data(account_number)
    await self._format_account_data()

    location_and_date_data = await self._build_location_and_date_data()
    update_data.update(location_and_date_data)

    programs_data = await self._get_programs_data(account_number)
    update_data.update(programs_data)

    monthly_data =  await self._get_monthly_data_from_energy_service(account_number)
    update_data.update(monthly_data)

    daily_data =  await self._get_daily_data_from_energy_service(account_number)
    update_data.update(daily_data)

    hourly_data = await self._get_hourly_data_from_energy_service(account_number)
    update_data.update(hourly_data)

    current_data = await self._get_current_data_from_energy_service(account_number)
    update_data.update(current_data)

    # app_usage_data = await self._get_data_from_appliance_usage(account_number)
    # update_data.update(app_usage_data)

    # balance_data = await self._get_data_from_balance(account_number)
    # update_data.update(balance_data)

    return update_data

  async def _get_account_data(self, account_number):
    async with async_timeout.timeout(TIMEOUT):
      response = await self.session.get(URL_RESOURCES_ACCOUNT.format(account=account_number))

    self.account_data = (await response.json())["data"]
    return

  async def _format_account_data(self):
    self.account_data["premiseNumber"] = self.account_data["premiseNumber"].zfill(9)
    self.account_data["currentBillDate"] = datetime.fromisoformat(self.account_data["currentBillDate"]).date()
    self.account_data["nextBillDate"] = datetime.fromisoformat(self.account_data["nextBillDate"]).date()

  async def _build_location_and_date_data(self):
    _LOGGER.debug(f'self = {self}') # TODO: Remove

    location_and_date_data = {}

    current_bill_date = self.account_data["currentBillDate"]
    next_bill_date = self.account_data["nextBillDate"]

    location_and_date_data["premise_number"] = self.account_data["premiseNumber"]
    location_and_date_data["meter_serial_no"] = self.account_data["meterSerialNo"]
    location_and_date_data["current_bill_date_as_str"] = str(current_bill_date)
    location_and_date_data["next_bill_date"] = str(next_bill_date)
    location_and_date_data["service_days"] = (next_bill_date - current_bill_date).days
    location_and_date_data["as_of_days"] = (date.today() - current_bill_date).days
    location_and_date_data["remaining_days"] = (next_bill_date - date.today()).days

    return location_and_date_data

  async def _get_programs_data(self, account_number):
    program_data = {}
    program_name_to_is_enrolled = {}

    for program in self.account_data["programs"]["data"]:
      if "enrollmentStatus" in program:
        key = program["name"]
        program_name_to_is_enrolled[key] = program["enrollmentStatus"] == ENROLLED

    # Budget Billing program
    program_data["budget_bill"] = False

    # TODO: Still not 100% what is happenening here, but don't care right now
    if program_name_to_is_enrolled["BBL"]:
      program_data["budget_bill"] = True
      bbl_data = await self._get_bbl_program_info(account_number)
      program_data.update(bbl_data)

    return program_data

  async def _get_bbl_program_info(self, account_number) -> dict:
    """Get budget billing program data from FPL."""
    _LOGGER.info("Getting budget billing data")
    data = {}

    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.get(
          URL_BUDGET_BILLING_PREMISE_DETAILS.format(account=account_number)
        )
        if response.status == 200:
          r = (await response.json())["data"]
          dataList = r["graphData"]

          # startIndex = len(dataList) - 1

          billingCharge = 0
          budgetBillDeferBalance = r["defAmt"]

          projectedBill = self.account_data["projectedBillData"]["projected_bill"]
          asOfDays = self.account_data["projectedBillData"]["as_of_days"]

          for det in dataList:
            billingCharge += det["actuallBillAmt"]

          calc1 = (projectedBill + billingCharge) / 12
          calc2 = (1 / 12) * (budgetBillDeferBalance)

          projectedBudgetBill = round(calc1 + calc2, 2)
          bbDailyAvg = round(projectedBudgetBill / 30, 2)
          bbAsOfDateAmt = round(projectedBudgetBill / 30 * asOfDays, 2)

          data["budget_billing_daily_avg"] = bbDailyAvg
          data["budget_billing_bill_to_date"] = bbAsOfDateAmt
          data["budget_billing_projected_bill"] = float(projectedBudgetBill)

      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.get(
          URL_BUDGET_BILLING_GRAPH.format(account=account_number)
        )
        if response.status == 200:
          r = (await response.json())["data"]
          data["bill_to_date"] = float(r["eleAmt"])
          data["defered_amount"] = float(r["defAmt"])
    except Exception as e:
      _LOGGER.error(e)

    return data

  async def _get_monthly_data_from_energy_service(self, account_number) -> dict:
    _LOGGER.info(f"Getting Monthly Data from {URL_ENERGY_SERVICE}")

    MONTHLY_ENERGY_SERVICE_JSON = {
      "billComparisionFlag": False,
      "frequencyType": "Monthly",
      "monthlyFlag": True,
      "projectedBillFlag": True,
    }

    results = { 'monthly_data': [] }
    try:
      async with async_timeout.timeout(TIMEOUT):
        response_data = await self._get_energy_service_data(account_number, MONTHLY_ENERGY_SERVICE_JSON)

        monthly_usage_response_data = response_data.get("MonthlyUsage", {}).get("data", [])

        if monthly_usage_response_data != []:
          if monthly_usage_response_data.get("exceptionDetails", {}) == {}:
            for monthly_data in monthly_usage_response_data:
              monthly_result = await self._build_monthly_usage(monthly_data)
              results['monthly_data'].append(monthly_result)
          else:
            exception_message = monthly_usage_response_data["exceptionDetails"]["resultInfo"]
            _LOGGER.info(f'{URL_ENERGY_SERVICE} responded with exceptionDetails: {exception_message}')

    except Exception as e:
      _LOGGER.error("Monthly data update failed:", e)

    return results

  async def _get_daily_data_from_energy_service(self, account_number) -> dict:
    _LOGGER.info(f"Getting Daily Data from {URL_ENERGY_SERVICE}")

    DAILY_ENERGY_SERVICE_JSON = {
      "frequencyType": "Daily",
      "lastBilledDate": str(self.account_data["currentBillDate"].strftime("%m%d%Y")),
      "premiseNumber": self.account_data["premiseNumber"]
    }

    results = { "daily_usage": [] }
    try:
      async with async_timeout.timeout(TIMEOUT):
        response_data = await self._get_energy_service_data(account_number, DAILY_ENERGY_SERVICE_JSON)
        daily_usage_response_data = response_data.get("DailyUsage",[]).get("data",[])

        if daily_usage_response_data != []:
          _LOGGER.debug(f'daily_usage_response_data = {daily_usage_data}') # TODO: Remove

          for daily_usage_data in daily_usage_response_data:
            if daily_usage_data["missingDay"] == "true": continue

            daily_result = await self._build_daily_usage(daily_usage_response_data)
            results["daily_usage"].append(daily_result)
        else:
          _LOGGER.info(f'{URL_ENERGY_SERVICE} responded with no DailyUsage data')

    except Exception as e:
      _LOGGER.error("Daily data fetch failed:", e)

    return results

  async def _get_hourly_data_from_energy_service(self, account_number) -> dict:
    HOURLY_ENERGY_SERVICE_JSON = {
      "frequencyType": "Hourly",
      "meterNo": self.account_data["meterSerialNo"],
      "premiseNumber": self.account_data["premiseNumber"],
      "startDate": date.today().strftime("%m%d%Y"),
    }

    results = { "hourly_usage": [] }
    try:
      async with async_timeout.timeout(TIMEOUT):
        response_data = await self._get_energy_service_data(account_number, HOURLY_ENERGY_SERVICE_JSON)
        hourly_usage_data = response_data.get("HourlyUsage", {}).get("data", [])

        if hourly_usage_data != []:
          hourly_data = await self._build_current_usage(hourly_usage_data)
          results["hourly_usage"].append(hourly_data)
        else:
          _LOGGER.info(f'{URL_ENERGY_SERVICE} responded with no CurrentUsage data')

    except Exception as e:
      _LOGGER.error("Current data fetch failed:", e)

    return results

  async def _get_current_data_from_energy_service(self, account_number) -> dict:
    _LOGGER.info(f"Getting Current Data from {URL_ENERGY_SERVICE}")

    CURRENT_ENERGY_SERVICE_JSON = {
      "amrFlag": "Y",
      "lastBilledDate": str(self.account_data["currentBillDate"].strftime("%m%d%Y")),
      "premiseNumber": self.account_data["premiseNumber"],
      "projectedBillFlag": True,
    }

    results = { "current_usage": {} }
    try:
      async with async_timeout.timeout(TIMEOUT):
        response_data = await self._get_energy_service_data(account_number, CURRENT_ENERGY_SERVICE_JSON)
        current_usage_data = response_data.get("CurrentUsage", {})

        if current_usage_data != {}:
          current_usage_result = await self._build_current_usage(current_usage_data)
          results["current_usage"] = current_usage_result
        else:
          _LOGGER.info(f'{URL_ENERGY_SERVICE} responded with no CurrentUsage data')

    except Exception as e:
      _LOGGER.error("Current data fetch failed:", e)

    return results

  async def _get_energy_service_data(self, account_number, json):
    url = URL_ENERGY_SERVICE.format(account=account_number)
    response = await self.session.post(url, json=json)

    if response.status != 200: raise f"FPL post to {URL_ENERGY_SERVICE} failed"

    response_data = (await response.json()).get("data",[])
    if response_data == []: raise f"FPL post to {URL_ENERGY_SERVICE} succeded but had no data"

    return response_data

  async def _build_monthly_usage(self, monthly_usage_data):
    results = []

    _LOGGER.debug(f'monthly_usage_data = {monthly_usage_data}') # TODO: Remove


      bill_start_date = datetime.fromisoformat(monthly_data["billStartDate"]).date()
      bill_end_date = datetime.fromisoformat(monthly_data["billEndDate"]).date()

      monthly_result = {
        "bill_start_date": bill_start_date,                                                 # "2024-07-05T00:00:00.000",
        "bill_end_date": bill_end_date,                                                     # "2024-08-05T00:00:00.000",
        "billing_charge":           float(monthly_data.get("billingCharge", 0.0)),          # 90.07,
        "temperature":              float(monthly_data.get("temperature", 0.0)),            # 91.0,
        "humidity":                 float(monthly_data.get("humidity", 0.0)),               # 94.0,
        "billed_kwh":               int(monthly_data.get("billedKwh", 0)),                  # 624,
        "billing_days":             int(monthly_data.get("billingDays", 0)),                # 31,
        "billing_month":            monthly_data.get("billingMonth", ""),                   # "Aug",
        "billing_year":             int(monthly_data.get("billingYear", 0)),                # "2024",
        "average_high_temperature": float(monthly_data.get("averageHighTemperature", 0.0)), # 91.0,
        "average_low_temperature":  float(monthly_data.get("averageLowTemperature", 0.0)),  # 76.0,
        "average_mid_temperature":  float(monthly_data.get("averageMidTemperature", 0.0)),  # 83.0,
        "average_high_humidity":    float(monthly_data.get("averageHighHumidity", 0.0)),    # 96.0,
        "average_low_humidity":     float(monthly_data.get("averageLowHumidity", 0.0)),     # 63.0,
        "average_mid_humidity":     float(monthly_data.get("averageMidHumidity", 0.0)),     # 81.0,
        "on_peak_kwh":              int(monthly_data.get("onPeakKwh", 0)),                  # 0,
        "off_peak_kwh":             int(monthly_data.get("offPeakKwh", 0)),                 # 0,
        "net_delivered":            int(monthly_data.get("netDelivered", 0)),               # 1243,
        "net_received":             int(monthly_data.get("netReceived", 0)),                # 522,
        "meter_number":             monthly_data.get("meterNumber", ""),                    # "KCD075N",
        "meter_type":               monthly_data.get("meterType", ""),                      # "Y",
        "reading":                  int(monthly_data.get("reading", 0)),                    # 26220,
        "net_delivered_reading":    int(monthly_data.get("netDeliveredReading", 0)),        # 26220,
        "net_received_reading":     int(monthly_data.get("netReceivedReading", 0)),         # 13539
      }

      results.append(monthly_result)

    return results

  async def _build_daily_usage(self, daily_usage_data):
    read_time = datetime.fromisoformat(daily_usage_data["readTime"])

    return {
      "kwh_used":        daily_usage_data["kwhUsed"],        # 2,
      "hour":            daily_usage_data["hour"],           # 1,
      "temperature":     daily_usage_data["temperature"],    # 86,
      "humidity":        daily_usage_data["humidity"],       # 82,
      "billing_charged": daily_usage_data["billingCharged"], # 0.27,
      "kwh_actual":      daily_usage_data["kwhActual"],      # 2.29,
      "read_time":       read_time,                          # "2024-08-02T01:00:00.000-04:00",
      "reading":         daily_usage_data["reading"],        # 27549.2604,
      "net_delivered":   daily_usage_data["netDelivered"],   # 2.29,
      "net_received":    daily_usage_data["netReceived"],    # 0
    }

  async def _build_current_usage(self, current_usage_data):
    _LOGGER.debug(f'current_usage_data = {current_usage_data}') # TODO: Remove

    date_format = '%m-%d-%Y'
    as_of_date = datetime.strptime(current_usage_data["asOfDate"], date_format).date()
    bill_start_date = datetime.strptime(current_usage_data["billStartDate"], date_format).date()
    bill_end_date = datetime.strptime(current_usage_data["billEndDate"], date_format).date()

    projected_bill_start_date = datetime.fromtimestamp(current_usage_data["projectedBillStartDate"] / 1e3).date()
    projected_bill_end_date = datetime.fromtimestamp(current_usage_data["projectedBillEndDate"] / 1e3).date()

    date_format = '%b %d, %Y'
    next_bill_date = datetime.strptime(current_usage_data["nextBillDate"], date_format).date()
    converted_start_date = datetime.strptime(current_usage_data["convertedStartDate"], date_format).date()
    converted_end_date = datetime.strptime(current_usage_data["convertedEndDate"], date_format).date()

    return {
      "projected_bill":            float(current_usage_data["projectedBill"]),               # "111.95",
      "service_days":              int(current_usage_data["serviceDays"]),                   # "33",
      "bill_to_date":              float(current_usage_data["billToDate"]),                  # "70.28",
      "as_of_days":                int(current_usage_data["asOfDays"]),                      # "21",
      "as_of_date":                as_of_date,                                               # "08-22-2024",
      "daily_avg":                 float(current_usage_data.get("dailyAvg", 0.0)),           # 3.35,
      "avg_high_temp":             float(current_usage_data.get("avgHighTemp", 0.0)),        # 94.0,
      "bill_start_date":           bill_start_date,                                          # "08-01-2024",
      "bill_end_date":             bill_end_date,                                            # "09-03-2024",
      "projected_kwh":             int(current_usage_data.get("projectedKWH", 0)),           # "842",
      "daily_average_kwh":         int(current_usage_data.get("dailyAverageKWH", 0)),        # "25",
      "bill_to_date_kwh":          int(current_usage_data.get("billToDateKWH", 0)),          # "536",
      "projected_kwh_rounded":     int(current_usage_data.get("projectedKWHRounded", 0)),    # "842",
      "projected_bill_start_date": projected_bill_start_date,                                # 1722484800000,
      "projected_bill_end_date":   projected_bill_end_date,                                  # 1725336000000,
      "avg_temp":                  int(current_usage_data.get("avgTemp", 0)),                # "84",
      "bill_diff":                 float(current_usage_data.get("billDiff", 0.0)),           # "15.57",
      "previous_bill_read":        int(current_usage_data.get("previousBillRead", 0)),       # "26220",
      "current_bill_read":         int(current_usage_data.get("currentBillRead", 0)),        # "27511",
      "today_meter_read":          int(current_usage_data.get("todayMeterRead", 0)),         # "28047",
      "previous_bill_amount":      float(current_usage_data.get("previousBillAmount", 0.0)), # "96.38",
      "delivered_meter_reading":   int(current_usage_data.get("delMtrReading", 0)),          # "27511",
      "recieved_meter_reading":    int(current_usage_data.get("recMtrReading", 0)),          # "14134",
      "next_bill_date":            next_bill_date,                                           # "Sep 03, 2024",
      "converted_start_date":      converted_start_date,                                     # "Aug 01, 2024",
      "converted_end_date":        converted_end_date,                                       # "Sep 03, 2024"
    }

  async def _get_data_from_appliance_usage(self, account_number) -> dict:
    """Get data from appliance usage."""
    _LOGGER.info("Getting appliance usage data")

    date = str(self.account_data["currentBillDate"].strftime("%m%d%Y"))
    JSON = { "startDate": date }
    data = {}

    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.post(
          URL_APPLIANCE_USAGE.format(account=account_number), json=JSON
        )
        if response.status == 200:
          electric = (await response.json())["data"]["electric"]

          full = 100
          for e in electric:
            rr = round(float(e["percentageDollar"]))
            if rr < full:
              full = full - rr
            else:
              rr = full
            data[e["category"].replace(" ", "_")] = rr
    except Exception as e:
      _LOGGER.error(e)

    return {"energy_percent_by_applicance": data}

  async def _get_data_from_balance(self, account_number) -> dict:
    """Get data from appliance usage."""
    _LOGGER.info("Getting appliance usage data")

    data = {}

    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.get(URL_BALANCE.format(account=account_number))
        if response.status == 200:
          data = (await response.json())["data"]

          # indice = [i for i, x in enumerate(data) if x["details"] == "DEBT"][
          #   0
          # ]

          # deb = data[indice]["amount"]

    except Exception as e:
      _LOGGER.error(e)

    return {"balance_data": data}
