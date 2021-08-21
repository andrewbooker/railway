#!/usr/bin/env python


import threading
import readchar
import sys
import time
from lib.navigator import Journey


layoutStr = None
if len(sys.argv) < 2:
    print("specify layout json file")
    exit()

with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

def say(*what):
    p = what[0]
    for i in range(1, len(what)):
        p = "%s %s" % (p, what[i])
    sys.stdout.write("%s\r\n" % p)

class NavigationListener():
    def __init__(self, detectionListener, directionController):
        self.detectionListener = detectionListener
        self.directionController = directionController
        self.currentDirection = "forward"
        self.currentSection = None

    @staticmethod
    def portId(p):
        return "%s_%s" % (p["bank"], p["port"])

    def _set(self):
        self.directionController.set(NavigationListener.portId(self.currentSection["direction"]), self.currentDirection)
        if "until" in self.currentSection:
            u = self.currentSection["until"]
            if self.currentDirection in u:
                d = u[self.currentDirection]
                self.detectionListener.setNextDetector(NavigationListener.portId(d), 1)


    def changeDirection(self, to):
        say("changing direction to", to)
        self.currentDirection = to
        self._set()

    def moveTo(self, section):
        say("setting section to", section["name"])
        self.currentSection = section
        self._set()

    def setPointsTo(self, s, p):
        #detectionListener.setNextDetector...
        say("setting points", p["name"], "to", s)

    def waitToSetPointsTo(self, s, p):
        say("setting points", p["name"], "to", s, "if ready")


class TrafficListener():
    def __init__(self, detectors):
        self.detectors = detectors
        self.callback = None
        self.detector = None
        self.requiredState = None

    def setCallback(self, c):
        self.callback = c

    def setNextDetector(self, d, state):
        self.detector = d
        self.requiredState = state
        say("waiting for", state, "on", d)

    def poll(self):
        if self.detector is None or self.callback is None:
            return
        if self.detectors.stateOf(self.detector) == self.requiredState:
            self.callback()

class DirectionRelays():
    def set(self, portId, direction):
        say("powering in", direction, "using", portId)

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


directionRelays = DirectionRelays()
detectors = KeyboardDetectors()
traffic = TrafficListener(detectors)
navigation = NavigationListener(traffic, directionRelays)
journey = Journey(layoutStr, navigation)
traffic.setCallback(journey.nextStage)


class ControlLoop():
    def __init__(self, c, i):
        self.c = c
        self.i = i

    def start(self, shouldStop):
        while not shouldStop.is_set():
            self.c()
            time.sleep(self.i)

controlLoop = ControlLoop(traffic.poll, 1.0)

from lib.cmd import Cmd, shouldStop

print("starting")

cmd = Cmd(detectors.onCmd)
threadables = [
    cmd,
    controlLoop
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

#del ports
print("stopped")
