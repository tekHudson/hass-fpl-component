"""FPL Main region data collection api client."""

import json
import logging
from datetime import datetime
import aiohttp
import async_timeout


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

  def __init__(self, username, password, loop, session) -> None:
    _LOGGER.debug("FplMainRegionApiClient __init__")
    _LOGGER.debug(f"{username}")
    _LOGGER.debug(f"{password}")
    """Initialize the class."""
    self.session = session
    self.username = username
    self.password = password
    self.loop = loop

  async def login(self):
    """Login into fpl."""
    # login and get account information

    _LOGGER.debug(f"{URL_LOGIN}")
    _LOGGER.debug(f"{self.username}")
    _LOGGER.debug(f"{self.password}")
    async with async_timeout.timeout(TIMEOUT):
      response = await self.session.get(
        URL_LOGIN,
        auth=aiohttp.BasicAuth(self.username, self.password),
      )

    if response.status == 200:
      return LOGIN_RESULT_OK

    if response.status == 401:
      json_data = json.loads(await response.text())

      if json_data["messageCode"] == LOGIN_RESULT_INVALIDUSER:
        return LOGIN_RESULT_INVALIDUSER

      if json_data["messageCode"] == LOGIN_RESULT_INVALIDPASSWORD:
        return LOGIN_RESULT_INVALIDPASSWORD

    return LOGIN_RESULT_FAILURE

  async def get_open_accounts(self):
    _LOGGER.debug("FplMainRegionApiClient. get_open_accounts")
    """Get open accounts. Returns array with active account numbers."""
    result = []

    async with async_timeout.timeout(TIMEOUT):
      response = await self.session.get(URL_RESOURCES_HEADER)

    json_data = await response.json()
    accounts = json_data["data"]["accounts"]["data"]["data"]

    for account in accounts:
      if account["statusCategory"] == STATUS_CATEGORY_OPEN:
        result.append(account["accountNumber"])

    return result

  async def logout(self):
    """Log out from FPL."""
    _LOGGER.info("Logging out")

    try:
      async with async_timeout.timeout(TIMEOUT):
        await self.session.get(URL_LOGOUT)
    except Exception as e:
      _LOGGER.error(e)

  async def update(self, account) -> dict:
    _LOGGER.debug("FplMainRegionApiClient.update")
    """Get data from resources endpoint."""
    data = {}

    account_data = await self.__get_account_data(account)

    location_and_date_data = await self.__build_location_and_date_data(account_data)
    data.update(location_and_date_data)

    programs_data = await self.__get_programs_data(account, account_data)
    data.update(programs_data)

    # projected_bill_data = await self.__get_projected_bill_data(account, account_data)
    # data.update(projected_bill_data)

    # daily_data =  await self.__getDailyDataFromEnergyService(account, premise, currentBillDate)
    # data.update(daily_data)

    # hourly_data = await self.__getHourlyDataFromEnergyService(account, premise, currentBillDate)
    # data.update(hourly_data)

    # app_usage_data = await self.__getDataFromApplianceUsage(account, currentBillDate))
    # data.update(app_usage_data)

    # balance_data = await self.__getDataFromBalance(account)
    # data.update(balance_data)

    return data

  async def __get_account_data(self, account):
    async with async_timeout.timeout(TIMEOUT):
      response = await self.session.get(URL_RESOURCES_ACCOUNT.format(account=account))

    return (await response.json())["data"]

  async def __build_location_and_date_data(self, account_data):
    data = {}

    current_bill_date = datetime.strptime(
      account_data["currentBillDate"].replace("-", "").split("T")[0], "%Y%m%d"
    ).date()

    next_bill_date = datetime.strptime(
      account_data["nextBillDate"].replace("-", "").split("T")[0], "%Y%m%d"
    ).date()

    data["premise_number"] = account_data.get("premiseNumber").zfill(9)
    data["meter_serial_no"] = account_data["meterSerialNo"]
    data["current_bill_date"] = str(current_bill_date)
    data["next_bill_date"] = str(next_bill_date)
    data["service_days"] = (next_bill_date - current_bill_date).days
    data["as_of_days"] = (datetime.now().date() - current_bill_date).days
    data["remaining_days"] = (next_bill_date - datetime.now().date()).days

    return data

  async def __get_programs_data(self, account, account_data):
    data = {}
    programs = []
    programs_data = account_data["programs"]["data"]

    for program in programs_data:
      if "enrollmentStatus" in program:
        key = program["name"]
        programs[key] = program["enrollmentStatus"] == ENROLLED

    def hasProgram(program_name) -> bool:
      return program_name in programs and programs[program_name]

    # Budget Billing program
    data["budget_bill"] = False

    if hasProgram("BBL"):
      data["budget_bill"] = True
      bbl_data = await self.__get_bbl_program_info(account, account_data)
      data.update(bbl_data)

    return data

  async def __get_projected_bill_data(self, account_data, currentBillDate) -> dict:
    """Get data from projected bill endpoint."""
    data = {}

    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.get(
          URL_RESOURCES_PROJECTED_BILL.format(
            account=account,
            premise=premise,
            lastBillDate=currentBillDate.strftime("%m%d%Y"),
          )
        )

      if response.status == 200:
        projectedBillData = (await response.json())["data"]

        billToDate = float(projectedBillData["billToDate"])
        projectedBill = float(projectedBillData["projectedBill"])
        dailyAvg = float(projectedBillData["dailyAvg"])
        avgHighTemp = int(projectedBillData["avgHighTemp"])

        data["bill_to_date"] = billToDate
        data["projected_bill"] = projectedBill
        data["daily_avg"] = dailyAvg
        data["avg_high_temp"] = avgHighTemp

    except Exception as e:
      _LOGGER.error(e)

    return data

  async def __get_bbl_program_info(self, account, projectedBillData) -> dict:
    """Get budget billing data."""
    _LOGGER.info("Getting budget billing data")
    data = {}

    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.get(
          URL_BUDGET_BILLING_PREMISE_DETAILS.format(account=account)
        )
        if response.status == 200:
          r = (await response.json())["data"]
          dataList = r["graphData"]

          # startIndex = len(dataList) - 1

          billingCharge = 0
          budgetBillDeferBalance = r["defAmt"]

          projectedBill = projectedBillData["projected_bill"]
          asOfDays = projectedBillData["as_of_days"]

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
          URL_BUDGET_BILLING_GRAPH.format(account=account)
        )
        if response.status == 200:
          r = (await response.json())["data"]
          data["bill_to_date"] = float(r["eleAmt"])
          data["defered_amount"] = float(r["defAmt"])
    except Exception as e:
      _LOGGER.error(e)

    return data

  async def __getHourlyDataFromEnergyService(self, account, premise, lastBilledDate) -> dict:
    JSON = {
      "status":2,
      "channel":"WEB",
      "amrFlag":"Y",
      "accountType":"RESIDENTIAL",
      "revCode":"1",
      "premiseNumber": premise,
      "meterNo": meter,
      "projectedBillFlag": False,
      "billComparisionFlag": False,
      "monthlyFlag": False,
      "frequencyType":"Hourly",
      # "lastBilledDate":"",
      "applicationPage":"resDashBoard",
      # "startDate":"08172024",
      # "endDate":""
    }

  async def __getDailyDataFromEnergyService(self, account, premise, lastBilledDate) -> dict:
    _LOGGER.info("Getting energy service data")

    date = str(lastBilledDate.strftime("%m%d%Y"))
    JSON = {
      "recordCount": 24,
      "status": 2,
      "channel": "WEB",
      "amrFlag": "Y",
      "accountType": "RESIDENTIAL",
      "revCode": "1",
      "premiseNumber": premise,
      "projectedBillFlag": True,
      "billComparisionFlag": True,
      "monthlyFlag": True,
      "frequencyType": "Daily",
      "lastBilledDate": date,
      "applicationPage": "resDashBoard",
    }

    data = {}
    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.post(
          URL_ENERGY_SERVICE.format(account=account), json=JSON
        )
        if response.status == 200:
          rd = await response.json()
          if "data" not in rd:
            return []

          r = rd["data"]
          dailyUsage = []

          # totalPowerUsage = 0
          if (
            "data" in rd
            and "DailyUsage" in rd["data"]
            and "data" in rd["data"]["DailyUsage"]
          ):
            dailyData = rd["data"]["DailyUsage"]["data"]
            for daily in dailyData:
              if daily["missingDay"] != "true":
                dailyUsage.append(
                  {
                    "usage": daily.get("kwhUsed", None),
                    "cost": daily.get("billingCharge", None),
                    # "date": daily["date"],
                    "max_temperature": daily.get("averageHighTemperature", None),
                    "netDeliveredKwh": daily.get("netDeliveredKwh", 0),
                    "netReceivedKwh": daily.get("netReceivedKwh", 0),
                    "readTime": datetime.fromisoformat(
                      daily[
                        "readTime"
                      ]  # 2022-02-25T00:00:00.000-05:00
                    ),
                  }
                )
              # totalPowerUsage += int(daily["kwhUsed"])

            # data["total_power_usage"] = totalPowerUsage
            data["daily_usage"] = dailyUsage

          currentUsage = r["CurrentUsage"]
          data["projectedKWH"] = currentUsage["projectedKWH"]
          data["dailyAverageKWH"] = float(currentUsage["dailyAverageKWH"])
          data["billToDateKWH"] = float(currentUsage["billToDateKWH"])
          data["recMtrReading"] = int(currentUsage["recMtrReading"] or 0)
          data["delMtrReading"] = int(currentUsage["delMtrReading"] or 0)
          data["billStartDate"] = currentUsage["billStartDate"]
    except Exception as e:
      _LOGGER.error(e)

    return data

  async def __getDataFromApplianceUsage(self, account, lastBilledDate) -> dict:
    """Get data from appliance usage."""
    _LOGGER.info("Getting appliance usage data")

    JSON = {"startDate": str(lastBilledDate.strftime("%m%d%Y"))}
    data = {}

    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.post(
          URL_APPLIANCE_USAGE.format(account=account), json=JSON
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

  async def __getDataFromBalance(self, account) -> dict:
    """Get data from appliance usage."""
    _LOGGER.info("Getting appliance usage data")

    data = {}


    try:
      async with async_timeout.timeout(TIMEOUT):
        response = await self.session.get(URL_BALANCE.format(account=account))
        if response.status == 200:
          data = (await response.json())["data"]

          # indice = [i for i, x in enumerate(data) if x["details"] == "DEBT"][
          #   0
          # ]

          # deb = data[indice]["amount"]

    except Exception as e:
      _LOGGER.error(e)

    return {"balance_data": data}
