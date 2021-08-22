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
    def __init__(self, detectionListener, directionController, pointsController):
        self.detectionListener = detectionListener
        self.directionController = directionController
        self.pointsController = pointsController
        self.currentDirection = "forward"
        self.currentSection = None
        self.nextRequestor = None

    @staticmethod
    def portId(p):
        return "%s_%s" % (p["bank"], p["port"])

    def _set(self):
        self.detectionListener.clearCallback()
        self.directionController.set(NavigationListener.portId(self.currentSection["direction"]), self.currentDirection)

        if self.currentSection["id"][0] == "p":
            say("now at points", self.currentSection["name"])
            self.nextRequestor()
            return

        if "until" in self.currentSection:
            u = self.currentSection["until"]
            if self.currentDirection in u:
                d = u[self.currentDirection]
                self.detectionListener.setCallback(self.nextRequestor)
                self.detectionListener.setNextDetector(NavigationListener.portId(d), 1)

        if "next" in self.currentSection:
            n = self.currentSection["next"]
            if self.currentDirection in n and n[self.currentDirection]["id"][0] == "p":
                points = pointsController.fromId(n[self.currentDirection]["id"])
                say("next will be points", points["name"])
                self.detectionListener.setCallback(self.nextRequestor)
                self.detectionListener.setNextDetector(NavigationListener.portId(points["detector"]), 0)


    def setNextRequestor(self, r):
        self.nextRequestor = r

    def changeDirection(self, to):
        say("changing direction to", to)
        self.currentDirection = to

    def moveTo(self, section):
        say("setting section to", section["name"])
        self.currentSection = section
        self._set()

    def setPointsTo(self, s, p):
        say("setting", p["name"], "to", s, "now")
        self.detectionListener.waitFor(NavigationListener.portId(p["detector"]), 1)

    def waitToSetPointsTo(self, s, p):
        say("setting", p["name"], "to", s, "when ready")
        self.detectionListener.setCallback(self.nextRequestor)
        self.detectionListener.setNextDetector(NavigationListener.portId(p["detector"]), 0)


class TrafficListener():
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

class DirectionRelays():
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

class PointsController():
    def __init__(self):
        self.points = {}

    def fromLayout(self, layout):
        for p in layout["points"]:
            self.points[p["id"]] = p

    def fromId(self, pId):
        return self.points[pId]


from lib.cmd import Cmd, shouldStop

pointsController = PointsController()
directionRelays = DirectionRelays()
detectors = KeyboardDetectors()
traffic = TrafficListener(detectors, shouldStop)
navigation = NavigationListener(traffic, directionRelays, pointsController)
journey = Journey(layoutStr, navigation)

pointsController.fromLayout(journey.layout)
navigation.setNextRequestor(journey.nextStage)

print("starting")
journey.start()

class ControlLoop():
    def __init__(self, c, i):
        self.c = c
        self.i = i

    def start(self, shouldStop):
        while not shouldStop.is_set():
            self.c()
            time.sleep(self.i)

controlLoop = ControlLoop(traffic.poll, 1.0)

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
