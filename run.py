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

from lib.rpiPorts import UsingRPi, ServoPwmPort
rpi = UsingRPi()

class GenericDetectors():
    def __init__(self, device, deviceName):
        self.device = device
        self.deviceName = deviceName
        self.ports = {}

    def _at(self, p):
        if p not in self.ports:
            self.ports[p] = self.device.input(int(p))
        return self.ports[p]

    def stateOf(self, of):
        (bank, port) = of.split("_")
        if bank != self.deviceName:
            return 0
        return 1 if self._at(port).get() else 0

class DirectionRelays(DirectionController):
    def __init__(self, ardu):
        self.a = ardu
        self.ports = {}

    def set(self, portId, direction):
        if portId not in self.ports:
            self.ports[portId] = self.a.output(int(portId.split("_")[1]))
        self.ports[portId].set(0 if direction == "forward" else 1)


from lib.arduinoPorts import UsingArduino
class ArduinoDetectors(GenericDetectors):
    def __init__(self, ardu):
        GenericDetectors.__init__(self, ardu, "arduino")

class RpiDetectors(GenericDetectors):
    def __init__(self, r):
        GenericDetectors.__init__(self, r, "RPi")


from lib.model import Model
class ServoPointsController(PointsController):
    def set(self, port, s):
        points = Points(rpi.servoPwmPort(port, Points.LEFT))
        points.set(s)


ard = UsingArduino()
pointsController = ServoPointsController()

#detectors = ArduinoDetectors(ard) # will eventually all be arduino but using RPi for first small layouts
detectors = RpiDetectors(rpi)
detectionRouter = DetectionRouter()
detectionListener = TrafficListener(detectors, detectionRouter)

model = Model(layoutStr)
allRpiDetectionPorts = [14, 15] #read this from the model
detectionListener.registerPorts(allRpiDetectionPorts, "RPi")


monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)


def say(*what):
    p = what[0]
    for i in range(1, len(what)):
        p = "%s %s" % (p, what[i])
    monitor.setMessage("%s\r\n" % p)


ds = [
    ("WEX", "arduino", 41),
    ("NR", "arduino", 43),
    ("NRLP", "arduino", 45),
    ("NRL", "arduino", 47)
]
directionRelays = DirectionRelays(ard)
sectionDirections = {}
def doNothing(ignoreDirection):
    pass

for d in ds:
    dd = type("%s_direction" % d[0], (), {})
    setattr(dd, "set", doNothing)
    sectionDirections[d[0]] = dd

startingSection = "WEX"
controlLoop = ControlLoop(detectionListener.poll, 0.1)
controller = MotionController(speed, sectionDirections, monitor, 70, startingSection)
navigator = RouteNavigator(model, directionRelays, detectionRouter, pointsController, controller)
iterator = RouteIterator(model, navigator)

def nextSection():
    iterator.next()
    #say(detectionRouter.awaiting)

class Cb():
    def exec(self):
        nextSection()


detectionRouter.setCallback(Cb())

print("starting")
nextSection()
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
