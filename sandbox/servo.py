#!/usr/bin/env python


import sys
import os
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()
sys.path.append(parentDir)
from lib.points import Points
from lib.rpiPorts import UsingRPi, ServoPwmPort
import time
import random

rpi = UsingRPi()
points = Points(rpi.servoPwmPort(15, Points.LEFT))
try:
    while True:
        time.sleep(3)
        points.left() if random.random() > 0.5 else points.right()

except KeyboardInterrupt:
    del rpi

