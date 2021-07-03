#!/usr/bin/env python

import json
import threading
import readchar
import sys
from random import randint

class Journey():
    def __init__(self, layout):
        self.layout = layout
        self.direction = "forward"
        self.history = []
        self._at(self.layout["sections"][0])

    def _find(self, id):
        if "points" in self.layout:
            for p in self.layout["points"]:
                if p["id"] == id:
                    return p
        for s in self.layout["sections"]:
            if s["id"] == id:
                return s
        return None

    def _at(self, s):
        self.section = s
        self.history.append(s["id"])
        print("now on", s["name"])

    def _changeDirection(self):
        self.direction = "forward" if self.direction == "reverse" else "reverse"

    def nextStage(self):
        print("from", self.section["name"])
        if "next" not in self.section:
            if self.section["id"][0] == "p":
                if self.direction == "forward":
                    choice = "%s_id" % self.section["param"] if "param" in self.section else ("left_id" if (randint(0, 1) > 0) else "right_id")
                    print("choosing", choice.split("_")[0])
                    self._at(self._find(self.section[choice]))
                else:
                    print("points expected to be", "left" if self.section["left_id"] == self.history[-2] else "right")
                    for s in self.layout["sections"]:
                        if "forward" in s["next"] and s["next"]["forward"]["id"] == self.section["id"]:
                            self._at(s)
        else:
            options = self.section["next"]
            if self.direction in options:
                self._at(self._find(options[self.direction]["id"]))
            else:
                self._changeDirection()
                print("changing direction to", self.direction)

layout = None
with open(sys.argv[1], "r") as layoutSpec:
    layout = json.loads(layoutSpec.read())

print("sections:", len(layout["sections"]))
print("points:", len(layout["points"]) if "points" in layout else 0)

journey = Journey(layout)

shouldStop = threading.Event()
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "n":
        journey.nextStage()
    if c == "q":
        shouldStop.set()
        print(journey.history)
        exit()
