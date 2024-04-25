"""Config flow for Twitch."""

from __future__ import annotations

import logging
from typing import Any, cast

from twitchAPI.helper import first
from twitchAPI.twitch import Twitch
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, FlowResult
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_TOKEN
from homeassistant.helpers import config_entry_oauth2_flow, config_validation as cv
from homeassistant.helpers.config_entry_oauth2_flow import LocalOAuth2Implementation

from .const import CONF_FOLLOWER, CONF_NEW_SUBSCRIBER, DOMAIN, LOGGER, OAUTH_SCOPES


def _schema_with_defaults(
    follower: bool | None = True, sub: bool | None = True
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_FOLLOWER,
                default=follower,
            ): cv.boolean,
            vol.Optional(
                CONF_NEW_SUBSCRIBER,
                default=sub,
            ): cv.boolean,
        }
    )


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle Twitch OAuth2 authentication."""

    DOMAIN = DOMAIN
    reauth_entry: ConfigEntry | None = None

    def __init__(self) -> None:
        """Initialize flow."""
        super().__init__()
        self.data: dict[str, Any] = {}

    # @staticmethod
    # @callback
    # def async_get_options_flow(
    #     config_entry: config_entries.ConfigEntry,
    # ) -> config_entries.OptionsFlow:
    #     """Get the options flow for this handler."""
    #     return TwitchOptionFlowHandler(config_entry)

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {"scope": " ".join([scope.value for scope in OAUTH_SCOPES])}

    async def async_oauth_create_entry(
        self,
        data: dict[str, Any],
    ) -> FlowResult:
        """Handle the initial step."""
        implementation = cast(
            LocalOAuth2Implementation,
            self.flow_impl,
        )

        client = await Twitch(
            app_id=implementation.client_id,
            authenticate_app=False,
        )
        client.auto_refresh_auth = False
        await client.set_user_authentication(
            data[CONF_TOKEN][CONF_ACCESS_TOKEN], scope=OAUTH_SCOPES
        )
        user = await first(client.get_users())
        assert user

        user_id = user.id

        if not self.reauth_entry:
            await self.async_set_unique_id(user_id)
            self._abort_if_unique_id_configured()

            data2 = self.async_create_entry(
                title=user.display_name,
                data=data,
                options={CONF_FOLLOWER: True, CONF_NEW_SUBSCRIBER: True},
            )
            LOGGER.info(f"Created new entry for {data2}")
            return data2

        if self.reauth_entry.unique_id == user_id:
            self.hass.config_entries.async_update_entry(
                self.reauth_entry,
                data=data,
                options={},
            )
            await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        return self.async_abort(
            reason="wrong_account",
            description_placeholders={"title": self.reauth_entry.title},
        )


# class TwitchOptionFlowHandler(config_entries.OptionsFlow):
#     """Twitch config flow options handler."""

#     def __init__(self, config_entry) -> None:
#         """Initialize Twitch options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(
#         self, user_input: dict[str, Any] | None = None
#     ) -> FlowResult:
#         """Manage the Twitch options."""
#         if user_input is not None:
#             self.hass.config_entries.async_update_entry(
#                 self.config_entry, data=self.config_entry.data, options=user_input
#             )
#             return self.async_create_entry(title="", data=user_input)

#         current_follower = self.config_entry.options.get(CONF_FOLLOWER, False)
#         current_new_subscriber = self.config_entry.options.get(
#             CONF_NEW_SUBSCRIBER, False
#         )

#         return self.async_show_form(
#             step_id="init",
#             data_schema=_schema_with_defaults(current_follower, current_new_subscriber),
#         )
