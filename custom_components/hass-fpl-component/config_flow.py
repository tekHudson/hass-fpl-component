"""Home Assistant Fpl integration Config Flow."""
import sys
import logging

from collections import OrderedDict
from voluptuous import Schema, Required
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import callback
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_NAME
from .const import (
  CONF_ACCOUNTS,
  CONF_TERRITORY,
  DEFAULT_CONF_PASSWORD,
  DEFAULT_CONF_USERNAME,
  DOMAIN,
  LOGIN_RESULT_OK,
  LOGIN_RESULT_FAILURE,
  LOGIN_RESULT_INVALIDUSER,
  LOGIN_RESULT_INVALIDPASSWORD,
)

from .fplapi import FplApi

_LOGGER = logging.getLogger(__package__)

try:
  from .secrets import DEFAULT_CONF_PASSWORD, DEFAULT_CONF_USERNAME
except:
  pass

@callback
def configured_instances(hass):
  """Return a set of configured SimpliSafe instances."""
  entites = []
  for entry in hass.config_entries.async_entries(DOMAIN):
    entites.append(f"{entry.data.get(CONF_USERNAME)}")
  return set(entites)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  """Fpl Config Flow Handler."""

  VERSION = 1
  CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

  def __init__(self):
    _LOGGER.info("ConfigFlow #__init__")
    """Initialize the class."""
    self._errors = {}

  async def async_step_user(self, user_input):  # pylint: disable=dangerous-default-value
    _LOGGER.info("ConfigFlow #async_step_user")
    """Handle a flow initialized by the user."""
    self._errors = {}

    if user_input is not None:
      _LOGGER.info(f"user_input = {user_input}")
      username = user_input[CONF_USERNAME]
      password = user_input[CONF_PASSWORD]

      if username not in configured_instances(self.hass):
        session = async_create_clientsession(self.hass)
        api = FplApi(username, password, session, loop=self.hass.loop)
        result = await api.login()

        if result == LOGIN_RESULT_OK:
          info = await api.get_basic_info()

          accounts = info[CONF_ACCOUNTS]

          # accounts = await api.async_get_open_accounts()
          await api.logout()

          user_input[CONF_ACCOUNTS] = accounts
          user_input[CONF_TERRITORY] = info[CONF_TERRITORY]

          return self.async_create_entry(title=username, data=user_input)

        if result == LOGIN_RESULT_INVALIDUSER:
          self._errors[CONF_USERNAME] = "invalid_username"

        if result == LOGIN_RESULT_INVALIDPASSWORD:
          self._errors[CONF_PASSWORD] = "invalid_password"

        if result == LOGIN_RESULT_FAILURE:
          self._errors["base"] = "failure"

      else:
        self._errors[CONF_NAME] = "name_exists"

      return await self._show_config_form(user_input)

    return await self._show_config_form(user_input)

  async def _show_config_form(self, user_input):
    _LOGGER.info("ConfigFlow #_show_config_form")
    """Show the configuration form to edit location data."""
    username = DEFAULT_CONF_USERNAME
    password = DEFAULT_CONF_PASSWORD
    _LOGGER.info(f"user_input = {user_input}")

    if user_input is not None:
      if CONF_USERNAME in user_input:
        username = user_input[CONF_USERNAME]
      if CONF_PASSWORD in user_input:
        password = user_input[CONF_PASSWORD]

    data_schema = OrderedDict()
    data_schema[Required(CONF_USERNAME, default=username)] = str
    data_schema[Required(CONF_PASSWORD, default=password)] = str

    _LOGGER.info(f"data_schema = {data_schema}")
    return self.async_show_form(step_id="user", data_schema=Schema(data_schema), errors=self._errors)

  async def async_step_import(self, _):  # pylint: disable=unused-argument
    _LOGGER.info("ConfigFlow #async_step_import")
    """Import a config entry.

    Special type of import, we're not actually going to store any data.
    Instead, we're going to rely on the values that are in config file.
    """
    if self._async_current_entries():
      return self.async_abort(reason="single_instance_allowed")

    return self.async_create_entry(title="configuration.yaml", data={})
