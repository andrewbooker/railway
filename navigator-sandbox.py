#!/usr/bin/env python

import json
import threading
import readchar

class Journey():
    def __init__(self, layout):
        self.layout = layout
        self.direction = "forward"
        self.section = self.layout["sections"][0]

    def _find(self, option):
        for s in self.layout["sections"]:
            if s["id"] == option["id"]:
                return s
        return None

    def nextStage(self):
        options = self.section["next"]
        if self.direction in options:
            self.section = self._find(options[self.direction])
            print(self.section["name"])

layout = None
with open("example-layouts/single-loop.json", "r") as layoutSpec:
    layout = json.loads(layoutSpec.read())

print(len(layout["sections"]), "sections")

journey = Journey(layout)

shouldStop = threading.Event()
while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "n":
        journey.nextStage()
    if c == "q":
        shouldStop.set()
        exit()
