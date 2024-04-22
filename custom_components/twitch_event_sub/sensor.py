"""Support for the Twitch stream status."""

from __future__ import annotations

from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.object.eventsub import ChannelFollowEvent
from twitchAPI.twitch import Twitch, TwitchUser

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CLIENT, DOMAIN, LOGGER, SESSION


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of chunk_size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize entries."""
    client = hass.data[DOMAIN][entry.entry_id][CLIENT]
    session = hass.data[DOMAIN][entry.entry_id][SESSION]

    # channels = entry.options[CONF_CHANNELS]

    entities: list[TwitchSensor] = []
    user = await first(client.get_users())
    entity = TwitchSensor(user, session, client)
    await entity.setup()
    entities.append(entity)

    async_add_entities(entities, True)


class TwitchSensor(SensorEntity):
    """Representation of a Twitch channel."""

    _attr_translation_key = "channel"

    def __init__(
        self, channel: TwitchUser, session: OAuth2Session, client: Twitch
    ) -> None:
        """Initialize the sensor."""
        self._client = client
        self._channel = channel

    async def setup(self) -> None:
        """Initialize the eventsub."""
        eventsub = EventSubWebsocket(self._client)
        eventsub.start()

        await eventsub.listen_channel_follow_v2(
            self._channel.id, self._channel.id, self.on_update
        )
        LOGGER.info(
            f"Setup ......................######################.....................!"
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
