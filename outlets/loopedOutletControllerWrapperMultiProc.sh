#!/usr/bin/env sh

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

#"2001032327445025188348e1e9162a46"
export LOG_LEVEL="INFO"
export DEVICE_UUIDS='["2012187176784690837348e1e9431f99","2001032327445025188348e1e9162a46"]'

python3 "$(dirname $0)/loopedOutletControllerMultiProc.py" \
  --iterations 5000 \
  --sleepTime 300 \
  --runTime 15 \
  -u "$MU" \
  -p "$MP" \
  -d "$DEVICE_UUIDS"

