#!/bin/sh
mv custom_components/*/manifest.json custom_components/twitch_event_sub/temp.json
jq --arg version "$1" -r '.version |= $version' custom_components/twitch_event_sub/temp.json > custom_components/twitch_event_sub/manifest.json
rm custom_components/*/temp.json