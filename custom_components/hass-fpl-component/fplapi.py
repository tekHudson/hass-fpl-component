"""Custom FPl api client."""
import sys
import json
import logging
import async_timeout
from .const import (
  CONF_ACCOUNTS,
  CONF_TERRITORY,
  FPL_MAINREGION,
  LOGIN_RESULT_FAILURE,
  LOGIN_RESULT_OK,
  TIMEOUT,
  URL_TERRITORY,
)

from .FplMainRegionApiClient import FplMainRegionApiClient
from .FplNorthwestRegionApiClient import FplNorthwestRegionApiClient

_LOGGER = logging.getLogger(__package__)

class FplApi:
  """A class for getting energy usage information from Florida Power & Light."""

  def __init__(self, username, password, session, loop):
    """Initialize the data retrieval. Session should have BasicAuth flag set."""
    self._username = username
    self._password = password
    self._session = session
    self._loop = loop
    self._account_data = None
    self._territory = None
    self.access_token = None
    self.id_token = None
    self.apiClient = None

  async def getTerritory(self):
    """Get territory."""
    if self._territory is not None:
      return self._territory

    headers = {"userID": f"{self._username}", "channel": "WEB"}
    async with async_timeout.timeout(TIMEOUT):
      response = await self._session.get(URL_TERRITORY, headers=headers)

    if response.status == 200:
      territoryArray = (await response.json())["data"]["territory"]

      if len(territoryArray) == 0:
        # returns main region by default in case no regions found
        return FPL_MAINREGION

      return territoryArray[0]

  def isMainRegion(self):
    """Return true if this account belongs to the main region, not northwest."""

    return self._territory == FPL_MAINREGION

  async def initialize(self):
    """Initialize the api client."""
    self._territory = await self.getTerritory()

    # set the api client based on user's territory
    if self.apiClient is None:
      if self.isMainRegion():
        self.apiClient = FplMainRegionApiClient(
          self._username, self._password, self._loop, self._session, self._account_data
        )
      else:
        self.apiClient = FplNorthwestRegionApiClient(
          self._username, self._password, self._loop, self._session
        )

  async def get_basic_info(self):
    """Return basic info for sensor initialization."""
    await self.initialize()
    data = {}
    data[CONF_TERRITORY] = self._territory
    data[CONF_ACCOUNTS] = await self.apiClient.get_open_accounts()

    return data

  async def async_get_data(self) -> dict:
    """Get data from fpl api."""
    await self.initialize()
    data = {}
    data[CONF_ACCOUNTS] = []

    data[CONF_TERRITORY] = self._territory
    login_result = await self.apiClient.login()

    if login_result == LOGIN_RESULT_OK:
      accounts = await self.apiClient.get_open_accounts()

      data[CONF_ACCOUNTS] = accounts
      for account in accounts:
        data[account] = await self.apiClient.update(account)

      await self.apiClient.logout()
    return data

  async def login(self):
    """Login to the api."""
    try:
      await self.initialize()
      # login and get account information
      return await self.apiClient.login()

    except Exception as exception:
      _LOGGER.error("Error %s : %s", exception, sys.exc_info()[0])
      return LOGIN_RESULT_FAILURE

  async def async_get_open_accounts(self):
    """Return open accounts."""
    self.initialize()
    return await self.apiClient.get_open_accounts()

  async def logout(self):
    """Log out from fpl."""
    return await self.apiClient.logout()
