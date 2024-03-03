#!/usr/bin/env python
import os
from lib.monitor import PowerMonitor
from lib.speed import Speed
from application.commandBasedMotionController import CommandBasedMotionController
from lib.directionController import DirectionController, Direction
from lib.rpiPorts import UsingRPi
from lib.arduinoPorts import UsingArduino
from lib.cmd import *

os.system("clear")
rpi = UsingRPi()
ard = UsingArduino()
monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)


class UniversalDirectionController(DirectionController):
    def __init__(self, device: UsingArduino):
        DirectionController.__init__(self)
        self.ports = {p: device.output(p) for p in [41, 43, 45, 47]}  # [41, 48, 50, 51] can read these direct out of Model from layout.json

    def set(self, portId, direction: Direction):
        DirectionController.set(self, portId, direction)
        for p in self.ports:
            self.ports[p].set(0 if direction == Direction.Forward else 1)


class Detector:
    def __init__(self, port, pos, callback):
        self.callback = callback
        self.pos = pos
        self.port = port
        self.state = 0

    def start(self):
        while not shouldStop.is_set():
            v = self.port.get()
            if v != self.state:
                self.callback(v, self.pos)
                self.state = v
            time.sleep(0.05)


directionController = UniversalDirectionController(ard)
controller = CommandBasedMotionController(speed, monitor.msg, 90, directionController)

all_detectors = {
    14: "WEX incoming (South)",
    15: "WEX outgoing (North)",
    8: "North return loop",
    21: None,
    22: None,
    23: None,
    24: None,
}


targets = [speed, Cmd(controller.onCmd)]
targets.extend(
    Detector(rpi.input(p), d if d is not None else str(p), lambda a, b: monitor.setMessage("%s %s" % (a, b)))
    for p, d in all_detectors.items()
)
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in targets]
[thread.start() for thread in threads]
[thread.join() for thread in threads]
del rpi
del ard
