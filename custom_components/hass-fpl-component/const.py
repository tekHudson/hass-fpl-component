"""Constants for fpl."""
#
TIMEOUT = 5
API_HOST = "https://www.fpl.com"
URL_TERRITORY = API_HOST + "/cs/customer/v1/territoryid/public/territory"
URL_LOGIN = API_HOST + "/api/resources/login"
URL_BUDGET_BILLING_GRAPH = API_HOST + "/api/resources/account/{account}/budgetBillingGraph"
URL_RESOURCES_PROJECTED_BILL = (API_HOST
  + "/api/resources/account/{account}/projectedBill"
  + "?premiseNumber={premise}&lastBilledDate={lastBillDate}")
URL_ENERGY_SERVICE = API_HOST + "/dashboard-api/resources/account/{account}/energyService/{account}"
URL_APPLIANCE_USAGE = API_HOST + "/dashboard-api/resources/account/{account}/applianceUsage/{account}"
URL_BUDGET_BILLING_PREMISE_DETAILS = API_HOST + "/api/resources/account/{account}/budgetBillingGraph/premiseDetails"
URL_RESOURCES_HEADER = API_HOST + "/api/resources/header"
URL_LOGOUT = API_HOST + "/api/resources/logout"
URL_RESOURCES_ACCOUNT = API_HOST + "/api/resources/account/{account}"
URL_BALANCE = API_HOST + "/api/resources/account/{account}/balance?count=-1"
URL_NW_GET_ACCOUNT_LIST = API_HOST + "/cs/gulf/ssp/v1/profile/accounts/list"
URL_NW_GET_ACCOUNT_SUMMARY = API_HOST + "/cs/gulf/ssp/v1/accountservices/account/{account}/accountSummary?balance=y"

# Base component constants
NAME = "HASS FPL Component"
DOMAIN = "hass-fpl-component"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
PLATFORMS = ["sensor"]
REQUIRED_FILES = [
  ".translations/en.json",
  "const.py",
  "config_flow.py",
  "manifest.json",
  "sensor.py",
]
ISSUE_URL = "https://github.com/tekHudson/hass-fpl-component/issues"
ATTRIBUTION = "Data provided by FPL."

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

DEFAULT_CONF_USERNAME = ""
DEFAULT_CONF_PASSWORD = ""


# Api login result
LOGIN_RESULT_OK = "OK"
LOGIN_RESULT_INVALIDUSER = "NOTVALIDUSER"
LOGIN_RESULT_INVALIDPASSWORD = "FAILEDPASSWORD"
LOGIN_RESULT_UNAUTHORIZED = "UNAUTHORIZED"
LOGIN_RESULT_FAILURE = "FAILURE"


CONF_TERRITORY = "territory"
CONF_ACCOUNTS = "account"

FPL_MAINREGION = "FL01"
FPL_NORTHWEST = "FL02"
