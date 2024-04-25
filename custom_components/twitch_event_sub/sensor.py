"""Support for the Twitch stream status."""

from __future__ import annotations

import json

from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.object.eventsub import ChannelFollowEvent
from twitchAPI.twitch import AuthType, Twitch, TwitchUser
import voluptuous as vol

from homeassistant.components.application_credentials import (
    ClientCredential,
    async_import_client_credential,
)
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_TOKEN
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_FOLLOWER,
    CONF_NEW_SUBSCRIBER,
    DOMAIN,
    ICON,
    LOGGER,
    OAUTH_SCOPES,
)


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of chunk_size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Optional(CONF_TOKEN): cv.string,
        vol.Optional(
            CONF_FOLLOWER,
            default=True,
        ): cv.boolean,
        vol.Optional(
            CONF_NEW_SUBSCRIBER,
            default=True,
        ): cv.boolean,
    }
)

ATTR_GAME = "game"
ATTR_TITLE = "title"
ATTR_FOLLOWING = "followers"
ATTR_VIEWS = "views"

STATE_OFFLINE = "offline"
STATE_STREAMING = "streaming"


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Twitch platform."""
    await async_import_client_credential(
        hass,
        DOMAIN,
        ClientCredential(config[CONF_CLIENT_ID], config[CONF_CLIENT_SECRET]),
    )
    if CONF_TOKEN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=config
            )
        )
    else:
        async_create_issue(
            hass,
            DOMAIN,
            "deprecated_yaml_credentials_imported",
            breaks_in_ha_version="2024.4.0",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="deprecated_yaml_credentials_imported",
            translation_placeholders={
                "domain": DOMAIN,
                "integration_title": "Twitch",
            },
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize entries."""

    client = hass.data[DOMAIN][entry.entry_id]
    user = await first(client.get_users())
    entity_registry = er.async_get(hass)
    existing_entities = [
        entity
        for entity_id, entity in entity_registry.entities.items()
        if entity.original_name == user.display_name
    ]

    LOGGER.info(f"Existing entity if: {existing_entities}")
    entity_ids = [entity.entity_id for entity in existing_entities]

    # Only call async_remove if there are entities to remove
    if entity_ids:
        entity_registry.async_remove(*entity_ids)

    xisting_entities = [
        entity
        for entity_id, entity in entity_registry.entities.items()
        if entity.original_name == user.display_name
    ]
    LOGGER.info(f"Existing entity ifleer: {xisting_entities}")

    sensor = TwitchSensor(user, client)
    await sensor.setup()
    async_add_entities([sensor], True)


class TwitchSensor(SensorEntity):
    """Representation of a Twitch channel."""

    _attr_icon = ICON

    def __init__(self, channel: TwitchUser, client: Twitch) -> None:
        """Initialize the sensor."""
        self._client = client
        self._channel = channel
        self._eventsub = EventSubWebsocket(self._client)
        self._enable_user_auth = client.has_required_auth(AuthType.USER, OAUTH_SCOPES)
        self._attr_name = channel.display_name
        self._attr_unique_id = channel.id

    async def reregister(self):
        """Reregister the entity."""
        LOGGER.info("Reregistering entity %s", self.entity_id)

    async def async_update(self) -> None:
        """Update device state."""
        followers = (await self._client.get_channel_followers(self._channel.id)).total
        self._attr_extra_state_attributes = {
            ATTR_FOLLOWING: followers,
            ATTR_VIEWS: self._channel.view_count,
        }
        if stream := (
            await first(self._client.get_streams(user_id=[self._channel.id], first=1))
        ):
            self._attr_native_value = STATE_STREAMING
            self._attr_extra_state_attributes[ATTR_GAME] = stream.game_name
            self._attr_extra_state_attributes[ATTR_TITLE] = stream.title
            if self._attr_entity_picture is not None:
                self._attr_entity_picture = self._attr_entity_picture.format(
                    height=24,
                    width=24,
                )
        else:
            self._attr_native_value = STATE_OFFLINE
            self._attr_extra_state_attributes[ATTR_GAME] = None
            self._attr_extra_state_attributes[ATTR_TITLE] = None
            self._attr_entity_picture = self._channel.profile_image_url

    async def setup(self) -> None:
        """Initialize the eventsub."""
        self._eventsub.start()

        await self._eventsub.listen_channel_follow_v2(
            self._channel.id, self._channel.id, self.on_update
        )
        LOGGER.info(
            "Setup ......................######################.....................!"
        )

    async def on_update(self, data: ChannelFollowEvent):
        """Our event happend, lets do things with the data we got."""
        self.hass.bus.fire(
            "twitch_event_sub_new_follower",
            {"name": data.event.user_name},
        )
        LOGGER.info(
            f"{data.event.user_name} now follows {data.event.broadcaster_user_name}!"
        )
