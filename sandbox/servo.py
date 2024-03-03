#!/usr/bin/env python

from _imports import *
from lib.hardwarePoints import HardwarePoints
from lib.rpiPorts import UsingRPi
import time
import random

port = int(sys.argv[1])
rpi = UsingRPi()
points = HardwarePoints(rpi, port)

lr = False
try:
    while True:
        time.sleep(2)
        if not lr:
            print("left")
            points.left()
        else:
            print("right")
            points.right()
        lr = not lr

except KeyboardInterrupt:
    del rpi

