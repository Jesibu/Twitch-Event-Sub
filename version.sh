#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# Set JSON file path
json_file="custom_components/twitch_event_sub/manifest.json"

# Check if the JSON file exists
if [ ! -f "$json_file" ]; then
    echo "Error: JSON file '$json_file' not found."
    exit 1
fi

# Extract version argument
version=$1

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install jq to use this script."
    exit 1
fi

# Update the "version" property in the JSON file
jq --arg new_version "$version" '.version = $new_version' "$json_file" > tmp.json && mv tmp.json "$json_file"

echo "Version in $json_file updated to $version"
