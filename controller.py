#!/usr/bin/env python

from lib.monitor import PowerMonitor
from lib.speed import Speed
from application.commandBasedMotionController import CommandBasedMotionController
from lib.detectors import Detector
from lib.directionController import DirectionController
from lib.rpiPorts import UsingRPi
from lib.arduinoPorts import UsingArduino
from lib.cmd import *

rpi = UsingRPi()
ard = UsingArduino()
monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)


def onPass(a, b):
    monitor.setMessage("points %s %s" % (a, b))


class UniversalDirectionController(DirectionController):
    def __init__(self, device: UsingArduino):
        DirectionController.__init__(self)
        self.ports = {p: device.output(p) for p in [41, 48, 50, 51]}  # can read these direct out of Model from layout.json

    def set(self, portId, direction):
        DirectionController.set(self, portId, direction)
        for p in self.ports:
            self.ports[p].set(0 if direction == "forwards" else 1)


directionController = UniversalDirectionController(ard)
controller = CommandBasedMotionController(speed, monitor.msg, 90, directionController)

cmd = Cmd(controller.onCmd)

targets = [
    speed,
    Detector(rpi.input(14), "A", onPass),  # optional because they happen to be on the layout. are not in layout.json
    Detector(rpi.input(15), "B", onPass),
    cmd
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in targets]

[thread.start() for thread in threads]
[thread.join() for thread in threads]

del rpi
del ard
