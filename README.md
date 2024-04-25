# Twitch-Event-Sub (Work in Progress)

This project is an integration of the Twitch EventSub Websocket API with Home Assistant. It allows you to monitor Twitch channels and react to events such as new followers, subscriptions, and more, directly from your Home Assistant instance.

## Twitch EventSub Websocket API

The Twitch EventSub Websocket API is a service provided by Twitch that allows developers to subscribe to a variety of events related to a Twitch account. These events include, but are not limited to, new followers, stream status changes, and user subscriptions.

This API uses Websockets, a protocol that provides full-duplex communication channels over a single TCP connection. This means that the server can send data to the client without the client explicitly requesting it, making it ideal for real-time updates.

## Integration with Home Assistant

This project integrates the Twitch EventSub Websocket API with Home Assistant, a popular open-source home automation platform. With this integration, Home Assistant can monitor Twitch channels and react to events as they happen.

For example, you can set up an automation that turns on your living room lights whenever your favorite Twitch streamer goes live, or sends you a notification when you receive a new follower.

## Subscribing to a Custom Event

To subscribe to a custom event in Home Assistant, you need to create an automation. Here's a basic example of how to do this:

1. Go to the Home Assistant dashboard.
2. Navigate to "Configuration" -> "Automations".
3. Click on the "Add Automation" button.
4. Choose "Start with an empty automation".
5. Fill in the basic information for your automation (name, description, etc.).
6. In the "Triggers" section, choose "Event".
7. In the "Event Type" field, enter the name of the Twitch event you want to subscribe to (for example, "twitch_event_sub_new_follower").
8. In the "Action" section, define what you want Home Assistant to do when the event is triggered.

```yaml
automation:
    - alias: Subscribe to Twitch Event
        trigger:
            platform: event
            event_type: twitch_event_sub_new_follower
        action:
            - service: notify.notify
                data:
                    message: "New follower on Twitch!"
```
## Events

| Event Type | Description |
|------------|-------------|
| twitch_event_sub_new_follower | Triggered when a new follower is detected on Twitch. |

## Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these guidelines:
1. Fork the repository and create a new branch.
2. Make your changes and test them thoroughly.
3. Submit a pull request with a clear description of your changes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
