#!/usr/bin/env sh

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

export MEROSS_USER="$MU"
export MEROSS_PASS="$MP"
export LOG_LEVEL="INFO"

RUN_TIME=${1:-10} # run for 5 seconds
SLEEP_TIME=${2:-50} # sleep for 60 seconds
ITERATIONS=${3:-0} # number of times to do it, 0 means forever but the counter breaks
DEVICE_UUIDS=${4:-${DEVICE_UUIDS:-'["ARRAY_OF_DEVICE_UUIDS_HERE"]'}}

scripture=$(find $(dirname $0) -name "*MultiProc.py" -type f | head -n 1)
# 2012188285114690837348e1e9431dae
python3 ${scripture} \
  --iterations ${ITERATIONS} \
  --sleepTime ${SLEEP_TIME} \
  --runTime ${RUN_TIME} \
  -d ${DEVICE_UUIDS}

