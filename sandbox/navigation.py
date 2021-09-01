#!/usr/bin/env python


import threading
import readchar
import sys
import os

parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()
sys.path.append(parentDir)
from lib.navigator import Journey

class Reporter():
    def __init__(self):
        self.loc = None
        self.direction = None

    def _set(self):
        direction = self.direction if self.direction is not None else "assumed forwards"
        if "direction" in self.loc:
            print("now at", self.loc["name"], direction, "on", self.loc["direction"]["bank"], self.loc["direction"]["port"])
        else:
            print("now at", self.loc["name"], direction, "on points")

    def connect(self, section, direction):
        if (self.loc is not None):
            print("from", self.loc["name"])
        self.loc = section
        self.direction = direction
        self._set()

    def setPointsTo(self, selection, stage, points):
        print("heading", stage, selection, points[stage]["selector"]["bank"], points[stage]["selector"]["port"])

    def waitToSetPointsTo(self, selection, stage, points):
        print("heading", stage, selection, "if clear", points[stage]["selector"]["bank"], points[stage]["selector"]["port"])


class AutoController():
    def __init__(self, journey):
        self.journey = journey
        self.stages = []

    def plan(self):
        if len(self.stages) == 3:
            self.stages.pop(0)
        
        
# plan a total of three sections where the first section is the current location (assuming nothing blocking for now while running only one train)
# because a section usually terminates in points, a typical plan will have five instructions:
# 1) move forward on current section
# 2) set points to section2 (eg left)
# 3) move forward on section2
# 4) set points to section3 (eg right)
# 5) move forard on section3

#Rules:
# next points can be changed when train has entered current section PROVIDED it is not currently travelling over the points.
# (this is a general rule: points cannot change when a train is on them. Detectors are placed over points mid way between the slider bar and the rail hinge)
# power can be supplied to a section only when there is nothing in it.        



layoutStr = None
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

reporter = Reporter()
journey = Journey(layoutStr, reporter)
journey.start()

shouldStop = threading.Event()
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "n":
        journey.nextStage()
    if c == "q":
        shouldStop.set()
        print(journey.history)
        exit()
