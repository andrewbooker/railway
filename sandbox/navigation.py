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
