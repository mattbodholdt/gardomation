#### Microgreens Irrigation

Use to control a Meross bulbs, even not homekit..


```sh
#!/usr/bin/env bash

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

# ["psychedelic", "psyc", "primary", "stealth", "normal", "random", "off"]
CG=${1:-"psychedelic"} # color group

export LOG_LEVEL="INFO"

$(dirname $0)/bulbControl.py -c "$CG" -u "$MU" -p "$MP"
```