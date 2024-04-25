"""Const for Twitch."""

import logging

from twitchAPI.twitch import AuthScope

from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)

PLATFORMS = [Platform.SENSOR]

OAUTH2_AUTHORIZE = "https://id.twitch.tv/oauth2/authorize"
OAUTH2_TOKEN = "https://id.twitch.tv/oauth2/token"

CONF_REFRESH_TOKEN = "refresh_token"

DOMAIN = "twitch_event_sub"
CLIENT = "client"
SESSION = "session"

SUBSCRIBE_EVENT_SUB_NEW_FOLLOWER = "twitch_event_sub_new_follower"
SUBSCRIBE_EVENT_SUB_NEW_SUBSCRIBER = "twitch_event_sub_new_subscriber"

CONF_FOLLOWER = "new_follower"
CONF_NEW_SUBSCRIBER = "new_subscriber"

OAUTH_SCOPES = [
    AuthScope.USER_READ_SUBSCRIPTIONS,
    AuthScope.USER_READ_FOLLOWS,
    AuthScope.MODERATOR_READ_FOLLOWERS,
]

ICON = "mdi:twitch"
