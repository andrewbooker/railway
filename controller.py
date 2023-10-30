#!/usr/bin/env python

import os
from lib.monitor import PowerMonitor
from lib.speed import Speed
from lib.motionController import MotionController
from lib.distribution import Direction
from lib.detectors import Detector
from lib.rpiPorts import UsingRPi
from lib.arduinoPorts import UsingArduino
os.system("clear")
print("")

portA = 12
portB = 18


rpi = UsingRPi()
ard = UsingArduino()

class TmpArd():
    def __init__(self):
        self.a = [
            ard.output(41),
            ard.output(43),
            ard.output(45),
            ard.output(47),
            ard.output(48),
            ard.output(49),
            ard.output(50),
            ard.output(51)
        ]

    def set(self, v):
        for a in self.a:
            a.set(v)


pwr = TmpArd()
monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)
direction = Direction(pwr)


def onPass(a, b):
    monitor.setMessage("points %s %s" % (a, b))


controller = MotionController(speed, {"any": direction}, monitor.msg, 70, "any")
detectorA = Detector(rpi.input(14), "A", onPass)
detectorB = Detector(rpi.input(15), "B", onPass)

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
