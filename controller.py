#!/usr/bin/env python

import math
import os
import threading
os.system("clear")
print("")

import time

class Detector():
    def __init__(self, port, pos, callback):
        self.callback = callback
        self.pos = pos
        self.port = port
        self.state = 0

    def start(self, shouldStop):
        while not shouldStop.is_set():
            v = self.port.get()
            if v != self.state:
                self.callback(v, self.pos)
                self.state = v
            time.sleep(0.05)

portA = 12
portB = 18

from lib.rpiPorts import PwmPort, Output, UsingRPi
rpi = UsingRPi()

from lib.monitor import PowerMonitor
from lib.speed import MotionController, Speed
from lib.distribution import Direction

monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)
direction = Direction(rpi.output(23))

controller = MotionController(speed, {"any": direction}, monitor, 70, "any")
detectorA = Detector(rpi.input(14), "A", controller.onPass)
detectorB = Detector(rpi.input(15), "B", controller.onPass)

from lib.cmd import *
cmd = Cmd(controller.onCmd)

targets = [
    speed,
    detectorA,
    detectorB,
    cmd
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in targets]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

del rpi
