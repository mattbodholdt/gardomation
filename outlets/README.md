#### Outlet Control

Use to control a Meross plug.  In this case, to control how long a pump runs to drive sprinkler irrigation for microgreens.

```txt
usage: loopedOutletController.py [-h] [-u MEROSSUSER] [-p MEROSSPASS] [-d DEVICEUUIDS] [-i ITERATIONS] [-s SLEEPTIME] [-r RUNTIME]

Use to control Meross devices. Handles a single outlet device at a time. TODO - add support for multiple devices and multithreading

optional arguments:
  -h, --help            show this help message and exit
  -u MEROSSUSER, --merossUser MEROSSUSER
                        Meross user name
  -p MEROSSPASS, --merossPass MEROSSPASS
                        Meross password
  -d DEVICEUUIDS, --deviceUUIDs DEVICEUUIDS
                        String List of Meross Device UUIDs, default []. Note this script doesn't really support multiple devices yet.
  -i ITERATIONS, --iterations ITERATIONS
                        Number of iterations to do, default is 1000
  -s SLEEPTIME, --sleepTime SLEEPTIME
                        Number of seconds to sleep between iterations, default is 900
  -r RUNTIME, --runTime RUNTIME
                        Number of seconds to leave the power on. Default is 30
```

##### Execution
Can't execute directly, needs to be a positional to python3.  Typical inputs in the example below (microgreensWrapper.sh).

```sh
#!/usr/bin/env sh

set -e 

if [ -z "$MU" ] || [ -z "$MP" ]; then
  echo "MU/MP variables must be set.."
  exit 1
fi

export LOG_LEVEL="INFO"
export DEVICE_UUIDS='["2001032327445025188348e1e9162a46"]'

python3 loopedOutletController.py \
  --iterations 10 \
  --sleepTime 15 \
  --runTime 30 \
  -u "$MU" \
  -p "$MP" \
  -d "$DEVICE_UUIDS"
```