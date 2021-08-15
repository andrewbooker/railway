#!/usr/bin/env python


from lib.points import Points
import time
import random

from lib.rpiPorts import UsingRPi

rpi = UsingRPi()

points = Points(24)
try:
    while True:
        time.sleep(3)
        points.left() if random.random() > 0.5 else points.right()

except KeyboardInterrupt:
    del points
    del rpi

