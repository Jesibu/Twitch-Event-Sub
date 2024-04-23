#!/bin/sh
mv custom_components/*/manifest.json custom_components/twitch_event_sub/temp.json
jq -r '.name |= "$1"' $GITHUB_WORKSPACE/custom_components/twitch_event_sub/temp.json > $GITHUB_WORKSPACE/custom_components/twitch_event_sub/manifest.json
rm custom_components/*/temp.json