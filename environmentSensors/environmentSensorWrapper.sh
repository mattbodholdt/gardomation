#!/usr/bin/env bash

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

./environmentSensorData.py -u "$MU" -p "$MP"
