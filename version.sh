#!/bin/sh
mv custom_components/*/manifest.json custom_components/*/temp.json
jq -r '.name |= "adar"' custom_components/*/temp.json > custom_components/*/manifest.json
rm custom_components/*/temp.json