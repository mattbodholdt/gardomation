#/usr/bin/env python3

import argparse
import asyncio
import atexit
import json
import logging
import multiprocessing
import os

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager


def configure_logging() -> logging.Logger:
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s', level=log_level)
    logging.debug("Log Level: " + str(logging.getLogger().getEffectiveLevel()
                                      ) + ".  To override, set LOG_LEVEL environment variable.")
    meross_root_logger = logging.getLogger("meross_iot")
    meross_root_logger.setLevel(log_level)
    return logging.getLogger()


async def meross_logout(manager, client) -> bool:
  # Close the manager and logout from http_api
  manager.close()
  await client.async_logout()
  return True


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Use to control Meross devices.  Handles a single outlet device at a time.  TODO - add support for multiple devices and multithreading')
    parser.add_argument("-u", "--merossUser", required=False, type=str, default=str(os.getenv('MU', "none@bunkemail.org")),
                        help="Meross user name")
    parser.add_argument("-p", "--merossPass", required=False, type=str, default=str(os.getenv('MP', "MerossControlPlanePw")),
                        help="Meross password")
    parser.add_argument("-d", "--deviceUUIDs", required=False, type=str, action="store", default=os.getenv('DEVICE_UUIDS', []), help="String array of Meross Device UUIDs, default %(default)s. Parsed as JSON.")
    parser.add_argument("-i", "--iterations", required=False, type=int, action="store", default=0, help="Number of iterations to do, default is %(default)s, 0 means forever.")
    parser.add_argument("-s", "--sleepTime", required=False, type=int, action="store", default=900, help="Number of seconds to sleep between iterations, default is %(default)s")
    parser.add_argument("-r", "--runTime", required=False, type=int, action="store", default=30, help="Number of seconds to leave the power on. Default is %(default)s")
    return parser.parse_args()


def log_action(device_name: str, action: str, action_time: int, iteration_count: int, total_iterations: float, logger: logging.Logger):
  logger.info(f"{device_name} - Turning {action} for {str(action_time)} seconds - Iteration {str(iteration_count)} of {str(total_iterations)}.")


async def run(loop_args, args, logger):
  async def run_loop(dev, logger, args, loop_count, iterations):

    log_action(dev.name, 'on', args.runTime, loop_count, iterations, logger)
    await dev.async_turn_on(channel=0)
    await asyncio.sleep( int(args.runTime) )
    log_action(dev.name, 'off', args.sleepTime, loop_count, iterations, logger)
    await dev.async_turn_off(channel=0)
    if loop_count < iterations:
      logger.info(f"{dev.name} - Sleeping {str(args.sleepTime)} seconds before next iteration.")
      await asyncio.sleep(args.sleepTime)
    else:
      logger.info("Final iteration, shutting down!")
  iterations = args.iterations
  if iterations == 0:
    iterations = float('Infinity')
  
  device_uuid = loop_args.get('deviceUUID', None)

  if device_uuid is None:
    raise Exception.mro(device_uuid)

  logger.info("device_uuid: " + str(device_uuid))
  # Setup the HTTP client API from user-password
  http_api_client = await MerossHttpClient.async_from_user_password(email=str(args.merossUser), password=str(args.merossPass))

  # Setup and start the device manager
  manager = MerossManager(http_client=http_api_client)
  await manager.async_init()
  
  atexit.register( meross_logout, manager, http_api_client)
  
  await manager.async_device_discovery(meross_device_uuid = device_uuid)
  devs = manager.find_devices(device_uuids = [device_uuid])

  logger.info(str(len(devs)) + " device(s) found")
  logger.debug(str(devs[0]))

  for dev in devs:
    # Update device status: this is needed only the very first time we play with this device (or if the connection goes down)
    await dev.async_update()

    loop_count = 0
    if iterations == True:
      while iterations:
        await run_loop(dev, logger, args, loop_count, iterations)
    elif loop_count < iterations:
      while loop_count < iterations:
        loop_count += 1
        await run_loop(dev, logger, args, loop_count, iterations)


def loop_it(loop_args, args, logger=configure_logging()): 
  loop = asyncio.get_event_loop()
  loop.run_until_complete(run(loop_args, args, logger))


def main(args, logger):
  device_uuids = json.loads(args.deviceUUIDs)
  count = len(device_uuids)
  logger.info("Starting " + str(count) + " processes for " + str(len(device_uuids)) + " deviceIds " + json.dumps(device_uuids))
  for i in range(count):
    iter_args = {
      'deviceUUID': device_uuids[i],
      'logger': logger
    }
    p = multiprocessing.Process(
      target=loop_it,
      args=(iter_args, args, logger),
      name='outletController-' + str(device_uuids[i]),
      daemon=False,
    )
    p.start()
    logger.info('Started: ' + str(p))


if __name__ == '__main__':
  main(args=parse_args(), logger=configure_logging())
