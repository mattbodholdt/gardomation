#!/usr/bin/env bash

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

export LOG_LEVEL="INFO"
export DEVICE_UUID="2012182891843290837348e1e94319e2"

python3 powerConsumption.py -u "$MU" -p "$MP"

