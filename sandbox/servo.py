#!/usr/bin/env python

from _imports import *
from lib.hardwarePoints import HardwarePoints
from lib.rpiPorts import UsingRPi
import time
import random

port = int(sys.argv[1])
rpi = UsingRPi()
points = HardwarePoints(rpi, port)
try:
    while True:
        time.sleep(3)
        points.left() if random.random() > 0.5 else points.right()

except KeyboardInterrupt:
    del rpi

