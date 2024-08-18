#!/usr/bin/env python3

from _imports import *
import threading
import readchar
from lib.model import Model
from lib.detectionRouter import DetectionListener
from lib.routeNavigator import RouteNavigator, MotionController, PointsController
from lib.directionController import DirectionController, Direction


class LocalPointsController(PointsController):
    def set(self, pId, s):
        print(f"setting points {pId} to {s}")


class LocalMotionController(MotionController):
    def withChangeDirectionCallback(self, cb):
        print("executing direction change callback")

    def onCheckpoint(self):
        print("reached checkpoint")


class LocalDetectionListener(DetectionListener):
    def setNextDetector(self, d, v, description):
        print("setting next detector", d, v, description)

    def waitFor(self, d, state, description):
        print("waiting for", d, state, description)


layoutStr = None
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

model = Model(layoutStr)
direction = DirectionController()
detection = LocalDetectionListener()
points = LocalPointsController()
motion = LocalMotionController()

navigator = RouteNavigator(model, direction, detection, points, motion)

start_section = None
for s, _ in model.sections.items():
    start_section = s
    break

print("starting at", start_section)

shouldStop = threading.Event()
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "c":
        navigator.connect({"id": start_section}, Direction.Forward)

    print("current direction:", direction.currentDirection(), "on", direction.currentPortId())
    if c == "q":
        shouldStop.set()
        exit()

