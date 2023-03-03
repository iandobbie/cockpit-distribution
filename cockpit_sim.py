#!/usr/bin/python3

import multiprocessing
#hack needed to stop inifinite spawning on MacOS once frozen
multiprocessing.freeze_support()

import time
import os
import sys

import Pyro4

from microscope.device_server import device, DeviceServer, DeviceServerOptions
from microscope.simulators.stage_aware_camera import simulated_setup_from_image
import cockpit
import logging
import microscope

multiprocessing = multiprocessing.get_context("spawn")


Pyro4.config.SERIALIZERS_ACCEPTED.add("pickle")
Pyro4.config.SERIALIZER = "pickle"


DEVICE_SERVER_PORT = 8000

TIMEOUT = 20  # seconds
JOIN_TIMEOUT = 10  # seconds

SIMULATION_IMAGE_FILEPATH = 'merged-zaber-rgb.jpg'
DEPOT_FILEPATH = 'cockpit_sim.depot'
CONFIG_FILEPATH = 'cockpit_sim.config'
CHANNELS_FILEPATH = 'channels-cockpit_sim'



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS,
        # and places our data files in a folder relative to that temp
        # folder named as specified in the datas tuple in the spec file
        base_path = os.path.join(sys._MEIPASS, 'cockpit')
    except Exception:
        # sys._MEIPASS is not defined, so use the original path
        base_path = '.'

    return os.path.join(base_path, relative_path)
#start microscope device server with correct config.

def start_device_server(exit_event: multiprocessing.Event) -> None:
   # print(resource_path(SIMULATION_IMAGE_FILEPATH))
    device_server_process = DeviceServer(
        device(
            simulated_setup_from_image,
            "localhost",
            DEVICE_SERVER_PORT,
            conf={"filepath": resource_path(SIMULATION_IMAGE_FILEPATH)},
        ),
        options=DeviceServerOptions(config_fpath="",
                                    logging_level= logging.WARNING,
                                    logging_dir=os.path.join(os.path.dirname(sys.argv[0]))),
        id_to_host={},
        id_to_port={},
        exit_event=exit_event,
    )
    device_server_process.start()

    def _device_server_is_ready() -> bool:
        # Test that all devices are ready.
        for obj_name in ["stage", "filterwheel", "camera"]:
            uri = "PYRO:" + obj_name + "@localhost:" + str(DEVICE_SERVER_PORT)
            proxy = Pyro4.Proxy(uri)
            try:
                proxy._pyroBind()
            except Exception:
                return False
        else:
            return True

    start_time = time.time()
    while (not _device_server_is_ready()
           and time.time() < start_time + TIMEOUT):
        time.sleep(1)
    if not _device_server_is_ready():
        raise RuntimeError("Failed to start the device server")

    return device_server_process

def main():


    exit_event = multiprocessing.Event()
    device_server_process = start_device_server(exit_event)

    configFile=open(resource_path(CONFIG_FILEPATH),"w")
    configFile.write('[global]\n')
    configFile.write('channel-files: '+resource_path(CHANNELS_FILEPATH)+'\n')
    configFile.close()
    cockpit.main([
        "cockpit",
        "--depot-file",
        resource_path(DEPOT_FILEPATH),
        "--config-file",
        resource_path(CONFIG_FILEPATH),
    ])

    exit_event.set()
    device_server_process.join(JOIN_TIMEOUT)
    if device_server_process.exitcode is None:  # join timedout
        device_server_process.kill()

if __name__ == "__main__":
    main()

