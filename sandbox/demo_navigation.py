#!/usr/bin/env python3

from _imports import *
import threading
import readchar
from lib.model import Model
from lib.detectionRouter import DetectionRouter
from lib.routeNavigator import RouteNavigator, MotionController, PointsController
from lib.directionController import DirectionController, Direction


class LocalPointsController(PointsController):
    def set(self, pId, selection):
        print(f"setting points {pId} to {selection}")


class LocalMotionController(MotionController):
    def __init__(self):
        self.direction_cb = None

    def withChangeDirectionCallback(self, cb):
        self.direction_cb = cb
        print("callback captured")
        return self

    def onCheckpoint(self):
        print("reached checkpoint")


class StatusPrinter:
    def setValue(self, v):
        print(v)


def simulateReceivingAwaited(d):
    for k in d.awaiting:
        portId, val = k
        d.receiveUpdate(portId, val)
        return

def callback():
    print("Callback called upon detection")

layoutStr = None
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

model = Model(layoutStr)
direction = DirectionController()
detection = DetectionRouter(StatusPrinter())
detection.setCallback(callback)
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

    if c == "d":
        simulateReceivingAwaited(detection)

    print("current direction:", direction.currentDirection(), "on", direction.currentPortId())
    print("current detection awaited:", detection.awaiting)
    if c == "q":
        shouldStop.set()
        exit()

