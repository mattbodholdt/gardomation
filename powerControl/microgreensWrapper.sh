#!/usr/bin/env sh

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

export LOG_LEVEL="INFO"
export DEVICE_UUIDS='["2001032327445025188348e1e9162a46"]'

python3 microgreens.py \
  --iterations 10 \
  --sleepTime 15 \
  --runTime 30 \
  -u "$MU" \
  -p "$MP" \
  -d "$DEVICE_UUIDS"

