"""Data Update Coordinator."""
import traceback
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .fplapi import FplApi
from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=1200)
_LOGGER: logging.Logger = logging.getLogger(__package__)

class FplDataUpdateCoordinator(DataUpdateCoordinator):
  """Class to manage fetching data from the API."""

  def __init__(self, hass: HomeAssistant, client: FplApi) -> None:
    _LOGGER.debug("FplDataUpdateCoordinator #__init__")
    """Initialize the class."""
    self.api = client
    self.platforms = []

    super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

  async def _async_update_data(self):
    _LOGGER.debug("FplDataUpdateCoordinator #_async_update_data")
    """Update data via library."""
    try:
      return await self.api.async_get_data()
    except Exception as exception:
      _LOGGER.error("Error %s : %s", exception, traceback.format_exc())
      raise UpdateFailed() from exception
