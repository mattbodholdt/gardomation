#/usr/bin/env python3

import argparse
import asyncio
import logging
import os

from meross_iot.controller.mixins.electricity import ElectricityMixin
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager


def configureLogging():
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s', level=log_level)
    logging.debug("Log Level: " + str(logging.getLogger().getEffectiveLevel()
                                      ) + ".  To override, set LOG_LEVEL environment variable.")
    meross_root_logger = logging.getLogger("meross_iot")
    meross_root_logger.setLevel(log_level)
    return logging.getLogger()


def parseArgs():
    parser = argparse.ArgumentParser(description='Use to control Meross devices')
    parser.add_argument("-u", required=False, type=str, default=str(os.getenv('MU', "none@bunkemail.org")),
                        help="Meross user name")
    parser.add_argument("-p", required=False, type=str, default=str(os.getenv('MP', "MerossControlPlanePw")),
                        help="Meross password")
    return parser.parse_args()


async def main(args, logger):
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=str(args.u), password=str(args.p))

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the devices that implement the electricity mixin
    await manager.async_device_discovery(meross_device_uuid=os.getenv('DEVICE_UUID'))

    devs = manager.find_devices(device_class=ElectricityMixin, device_uuids=[os.getenv('DEVICE_UUID')])

    if len(devs) < 1:
        logger.error("No electricity-capable device found...")
    else:
        dev = devs[0]

        # Update device status: this is needed only the very first time we play with this device (or if the
        #  connection goes down)
        await dev.async_update()

        # Read the electricity power/voltage/current
        instant_consumption = await dev.async_get_instant_metrics()
        logger.info(f"Current consumption data: {instant_consumption}")

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()


def run():
    # if os.name == 'nt':
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    print(str(loop))
    loop.run_until_complete(main(args=parseArgs(), logger=configureLogging()))
    loop.close()


if __name__ == '__main__':
    run()