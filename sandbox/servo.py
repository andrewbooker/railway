#!/usr/bin/env python

import sys
import os
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()
sys.path.append(parentDir)
from lib.hardwarePoints import HardwarePoints
from lib.rpiPorts import UsingRPi, ServoPwmPort
import time
import random

port = int(sys.argv[1])

rpi = UsingRPi()
points = HardwarePoints(rpi.servoPwmPort(port, HardwarePoints.LEFT))
try:
    while True:
        time.sleep(3)
        points.left() if random.random() > 0.5 else points.right()

except KeyboardInterrupt:
    del rpi

