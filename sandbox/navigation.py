#!/usr/bin/env python3

import threading
import readchar
import sys
import os
import random
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()
sys.path.append(parentDir)
from lib.model import Model
from lib.routeIterator import RouteIterator, NavigationListener, PointsSelector


class DescriptiveNavigationListener(NavigationListener):
    def connect(self, section, direction):
        print("connecting", section, direction)

    def setPointsTo(self, s, st, p):
        print("setting points", s, st, p)

    def waitToSetPointsTo(self, s, st, p):
        print("waiting to set points", s, st, p)


class RandomPointsSelector(PointsSelector):
    def select(self):
        print("selection required")
        return "left" if random.random() > 0.5 else "right"


layoutStr = None
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

model = Model(layoutStr)
listener = DescriptiveNavigationListener()
points_selector = RandomPointsSelector()
route_iterator = RouteIterator(model, listener, points_selector)

shouldStop = threading.Event()
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "n":
        route_iterator.next()
    if c == "q":
        shouldStop.set()
        exit()
