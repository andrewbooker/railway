#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.join(os.getcwd(), "lib"))
from lib.routeIterator import RouteIterator
from lib.routeNavigator import *
from lib.detectionRouter import DetectionRouter
from lib.speed import MotionController, Speed
from lib.distribution import Direction
from lib.monitor import PowerMonitor
from lib.cmd import *

import threading
import readchar
import time


layoutStr = None
if len(sys.argv) < 2:
    print("specify layout json file")
    exit()
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

class TrafficListener():
    def __init__(self, detectorInputs, detectionRouter):
        self.detectionRouter = detectionRouter
        self.detectorInputs = detectorInputs
        self.detectorPorts = []

    def registerPorts(self, ports, bank):
        for p in ports:
            self.detectorPorts.append("%s_%d" % (bank, p))

    def poll(self):
        for d in self.detectorPorts:
            self.detectionRouter.receiveUpdate(d, self.detectorInputs.stateOf(d))

class Detector():
    def __init__(self):
        self.state = 0

from lib.rpiPorts import UsingRPi
rpi = UsingRPi()

class DirectionRelays(DirectionController):
    def __init__(self, ardu):
        self.a = ardu
        self.ports = {}

    def set(self, portId, direction):
        if portId not in self.ports:
            self.ports[portId] = self.a.output(int(portId.split("_")[1]))
        say(direction, "at", portId)
        self.ports[portId].set(direction)


from lib.arduinoPorts import UsingArduino
class ArduinoDetectors():
    def __init__(self, ardu):
        self.a = ardu
        self.ports = {}

    def _at(self, p):
        if p not in self.ports:
            self.ports[p] = self.a.input(int(p))
        return self.ports[p]

    def stateOf(self, of):
        (bank, port) = of.split("_")
        if bank != "arduino":
            return 0
        return 1 if self._at(port).get() else 0


from lib.model import Model
class StdoutPointsController(PointsController):
    def set(self, port, s):
        say("setting", port, "to", s)

ard = UsingArduino()
pointsController = StdoutPointsController()

detectors = ArduinoDetectors(ard)
detectionRouter = DetectionRouter()
detectionListener = TrafficListener(detectors, detectionRouter)

model = Model(layoutStr)
allRpiDetectionPorts = [14, 15] #read this from the model
detectionListener.registerPorts(allRpiDetectionPorts, "rpi")


monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)


def say(*what):
    p = what[0]
    for i in range(1, len(what)):
        p = "%s %s" % (p, what[i])
    monitor.setMessage("%s\r\n" % p)

directionRelays = DirectionRelays(ard)
wd = type("WEX_direction", (), {})
setattr(wd, "set", lambda d: directionRelays.set("ignoredString_49", d)) # read from model
sectionDirections = {
    "WEX": wd
}

startingSection = "WEX"
controlLoop = ControlLoop(detectionListener.poll, 0.1)
controller = MotionController(speed, sectionDirections, monitor, 70, startingSection)
navigator = RouteNavigator(model, directionRelays, detectionRouter, pointsController)
iterator = RouteIterator(model, navigator)

def next():
    iterator.next()
    say(detectionRouter.awaiting)

detectionRouter.setCallback(next)

print("starting")

def doNothing(c):
    pass

from lib.cmd import *
cmd = Cmd(controller.onCmd)
threadables = [
    speed,
    cmd,
    controlLoop
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

#del ports
print("stopped")
