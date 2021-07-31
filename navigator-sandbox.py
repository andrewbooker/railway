#!/usr/bin/env python


import threading
import readchar
import sys
from lib.navigator import Journey

class Reporter():
    def __init__(self):
        self.loc = None
        self.direction = None

    def changeDirection(self, to):
        self.direction = to
        print("changing direction to", to)

    def moveTo(self, sectionName):
        if (self.loc is not None):
            print("from", self.loc)
        print("now at", sectionName, self.direction if self.direction is not None else "")
        self.loc = sectionName

    def setPointsTo(self, p):
        print("heading", p)

    def waitToSetPointsTo(self, p):
        print("heading", p, "if clear")



layoutStr = None
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

reporter = Reporter()
journey = Journey(layoutStr, reporter)

shouldStop = threading.Event()
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "n":
        journey.nextStage()
    if c == "q":
        shouldStop.set()
        print(journey.history)
        exit()
