#!/usr/bin/env python3

from _imports import *
import threading
import readchar
import random
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
        s = "left" if 0 != (int(random.random() * 10) % 2) else "right"
        print("selection required:", s)
        return s


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
        section = model.sections[route_iterator.current[0]]
        print("Current:", section.name)
        print("Forward until:", section.forwardUntil)
        print("Reverse until:", section.reverseUntil)
    if c == "q":
        shouldStop.set()
        exit()
