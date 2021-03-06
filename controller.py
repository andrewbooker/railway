#!/usr/bin/env python

import math
import os
import threading
os.system("clear")
print("")

portA = 12
portB = 18

from lib.rpiPorts import PwmPort, Output, UsingRPi
rpi = UsingRPi()

from lib.monitor import PowerMonitor
from lib.speed import MotionController, Speed
from lib.distribution import Direction
from lib.detectors import Detector

monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)
direction = Direction(rpi.output(23))

controller = MotionController(speed, {"any": direction}, monitor, 70, "any")
detectorA = Detector(rpi.input(14), "A", controller.onPass)
detectorB = Detector(rpi.input(15), "B", controller.onPass)

from lib.cmd import *
cmd = Cmd(controller.onCmd)
controlLoop = ControlLoop(lambda: controller.onCmd('d'), 64)

targets = [
    speed,
    detectorA,
    detectorB,
    cmd,
    controlLoop
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in targets]

[thread.start() for thread in threads]
[thread.join() for thread in threads]


del rpi
