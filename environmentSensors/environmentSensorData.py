#!/usr/bin/env python3


import argparse
import asyncio
from datetime import datetime, timedelta
import json
import logging
import os
from time import sleep

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from meross_iot.model.enums import OnlineStatus


def configure_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s', level=log_level)
    logging.debug("Log Level: " + str(logging.getLogger().getEffectiveLevel()
                                      ) + ".  To override, set LOG_LEVEL environment variable.")
    meross_root_logger = logging.getLogger("meross_iot")
    meross_root_logger.setLevel(log_level)
    return logging.getLogger()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Get environment sensor readings from meross devices.  Loops through any sensors found and outputs to stdout')
    parser.add_argument("-u", required=False, type=str, default=str(os.getenv('MU', "none@bunkemail.org")),
                        help="Meross user name")
    parser.add_argument("-p", required=False, type=str, default=str(os.getenv('MP', "MerossControlPlanePw")),
                        help="Meross password")
    parser.add_argument("--deviceUUID", "-d", required=False, type=str, default=None,
                        help="Meross Hub UUID, default is %(default)s.  If None, will try discovery")
    parser.add_argument("--deviceType", "-t", required=False, type=str, default="ms100",
                        help="Device model, default is %(default)s")
    parser.add_argument("--iterations", "-i", required=False, type=int,
                        default=5, help="Number of iterations, default is %(default)s")
    parser.add_argument("--interval", required=False, type=int,
                        default=30, help="Interval between iteration executions, default is %(default)s")
    return parser.parse_args()


async def main(args, logger):

    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=args.u, password=args.p)

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    if (args.deviceUUID is not None):
      await manager.async_device_discovery(update_subdevice_status=True, meross_device_uuid=str(args.deviceUUID))
      sensors = manager.find_devices(
        device_type=args.deviceType, 
        online_status=OnlineStatus.ONLINE,
        device_uuids=[str(args.deviceUUID)] )
    else:
      await manager.async_device_discovery(update_subdevice_status=True)
      sensors = manager.find_devices(
        device_type=args.deviceType, 
        online_status=OnlineStatus.ONLINE )
    # Retrieve all the MS100 devices that are registered on this account
    
    if len(sensors) < 1:
        raise Exception("No online sensors found.")

    output = {}
    for sensor in sensors:
      output[str(sensor.name).replace(' ', '_')] = []

    for sensor in sensors:
      # loop thorough the active devices
      count = 0
      logger.info("Running for " + str(args.iterations) + " iterations..")
      while count < int(args.iterations):
        count += 1
        start = datetime.now()
        td = timedelta(seconds=args.interval)
        the_future = start + td

        logger.info("Iteration " + str(count) + ", " + str(td))


        cnt = 0
        for dev in sensors:
          cnt += 1
          logger.info("Device " + str(cnt) + " of " + str(len(sensors)) + " - " + dev.name + " - " + sensor.name)

          # Manually force and update to retrieve the latest temperature sensed from
          # the device. This ensures we get the most recent data and not a cached value
          await dev.async_update()

          # Access read cached data
          tempC = dev.last_sampled_temperature or 0
          tempF = (tempC * 1.8) + 32
          humid = dev.last_sampled_humidity
          time = dev.last_sampled_time

          data = {"tempF": tempF, "tempC": tempC, "humidity": humid, "sampleTime": time, "uuid": dev.uuid}
          logger.info(
              f"Current sampled data on {time}: " + json.dumps(data, indent=0, sort_keys=False, default=str))
          output[str(sensor.name).replace(' ', '_')].append(data)
          logger.info(str(cnt) + " of " + str(len(sensors)) + " devices complete for iteration " + str(count) + " of " + str(args.iterations))

        now = datetime.now()
        if count == args.iterations:
          logger.info("Final iteration complete!")
        elif the_future >= now:
          st = (the_future - now).total_seconds()
          logger.info('Sleeping for ' + str(st) + ' seconds')
          sleep(st)
        else:
          logger.info('Execution time exceeded interval, running again immediately')
    # Close the manager and logout from http_api
    print(json.dumps(output, sort_keys=False, default=str))
    manager.close()
    await http_api_client.async_logout()


if __name__ == '__main__':
    configure_logging()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args=parse_args(), logger=logging.getLogger()))
    loop.close()
