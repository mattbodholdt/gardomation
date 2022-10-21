#!/usr/bin/env sh

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi


export MEROSS_USER="$MU"
export MEROSS_PASS="$MP"
export LOG_LEVEL="INFO"

RUN_TIME=${1:-5} # run for 5 seconds
SLEEP_TIME=${2:-60} # sleep for 60 seconds
ITERATIONS=${3:-1000} # do it a thousand times

DEVICE_UUIDS='["YOURDEVICEUUIDHERE","ANOTHERDEVICEUUIDHEREETC"]'


python3 "$(dirname $0)/loopedOutletControllerMultiProc.py" \
  --iterations ${ITERATIONS} \
  --sleepTime ${SLEEP_TIME} \
  --runTime ${RUN_TIME} \
  -d "$DEVICE_UUIDS"

