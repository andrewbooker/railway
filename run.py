#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.join(os.getcwd(), "lib"))
from lib.routeIterator import RouteIterator
from lib.routeNavigator import *


import threading
import readchar
import time


layoutStr = None
if len(sys.argv) < 2:
    print("specify layout json file")
    exit()

manualTest = True if len(sys.argv) < 3 else False
print("Using", "keyboard control" if manualTest else "Arduino")

with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

def say(*what):
    p = what[0]
    for i in range(1, len(what)):
        p = "%s %s" % (p, what[i])
    sys.stdout.write("%s\r\n" % p)


class TrafficListener(DetectionListener):
    def __init__(self, detectors, shouldStop):
        self.shouldStop = shouldStop
        self.detectors = detectors
        self.callback = None
        self.detector = None
        self.requiredState = None

    def setCallback(self, c):
        self.callback = c

    def clearCallback(self):
        self.callback = None

    def setNextDetector(self, d, state):
        self.detector = d
        self.requiredState = state
        say("waiting for", state, "on", d)

    def waitFor(self, d, state):
        self.detector = None
        self.callback = None
        say("blocking wait for", state, "on", d)
        while self.detectors.stateOf(d) != state and not self.shouldStop.is_set():
            time.sleep(0.05)

    def poll(self):
        if self.detector is None or self.callback is None:
            return
        if self.detectors.stateOf(self.detector) == self.requiredState:
            self.callback()

class DirectionRelays(DirectionController):
    def set(self, portId, direction):
        say(direction, "at", portId)

class Detector():
    def __init__(self):
        self.state = 0


class KeyboardDetectors():
    def __init__(self):
        self.lookup = {
            "RPi_14": "1",
            "RPi_15": "2"
        }
        self.detectors = {}

    def stateOf(self, of):
        if of not in self.lookup:
            return 0
        c = self.lookup[of]
        if c not in self.detectors:
            return 0
        return self.detectors[c].state

    def onCmd(self, c):
        if c not in self.detectors:
            self.detectors[c] = Detector()
        self.detectors[c].state = 0 if self.detectors[c].state == 1 else 1


from lib.arduinoPorts import UsingArduino
class ArduinoDetectors():
    def __init__(self):
        self.a = UsingArduino()
        self.ports = {}

    def _at(self, p):
        if p not in self.ports:
            self.ports[p] = self.a.input(int(p))
        return self.ports[p]

    def stateOf(self, of):
        (bank, port) = of.split("_")
        if bank != "arduino":
            return 0
        return self._at(port).get()


from lib.model import Model
class StdoutPointsController(PointsController):
    def set(self, port, s):
        say("setting", port, "to", s)


def screenTest():
    return (KeyboardDetectors(), DirectionRelays(), StdoutPointsController())

def arduinoTest():
    return (ArduinoDetectors(), DirectionRelays(), StdoutPointsController())

(detectors, directionController, pointsController) = screenTest() if manualTest else arduinoTest()
from lib.cmd import *
detectionListener = TrafficListener(detectors, shouldStop)
model = Model(layoutStr)
navigator = RouteNavigator(model, directionController, detectionListener, pointsController)
iterator = RouteIterator(model, navigator)
navigator.setNextRequestor(iterator.next)


print("starting")
iterator.next()
controlLoop = ControlLoop(detectionListener.poll, 0.1)

def doNothing(c):
    pass

cmd = Cmd(detectors.onCmd if manualTest else doNothing)
threadables = [
    cmd,
    controlLoop
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

#del ports
print("stopped")
