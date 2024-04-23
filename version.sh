#!/bin/sh
mv custom_components/*/manifest.json custom_components/*/temp.json
jq -r '.name |= "$1"' $GITHUB_WORKSPACE/custom_components/*/temp.json > $GITHUB_WORKSPACE/custom_components/*/manifest.json
rm custom_components/*/temp.json