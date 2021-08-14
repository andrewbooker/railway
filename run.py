#!/usr/bin/env python

from lib.cmd import *
import sys
import threading


def say(what):
    sys.stdout.write("%s\r\n" % what)

class RoutingController():
    def __init__(self, instructionProvider, layout):
        self.instructions = []
        self.currentInstruction = None
        self.layout = layout
        self.instructionProvider = instructionProvider
        self.checkpoints = {}
        self.sections = {}
        self.points = {}

    def _attemptNext(self):
        if len(self.instructions) == 0:
            return

        ins = self.instructions[0]
        if self.currentInstruction is not None:                
            sectionLayout = self.layout[ins.name] # so far only have section instructions
            until = sectionLayout["until"]
            if until is None or until[ins.direction] is None or until[ins.direction].state() == 0:
                return
            
        print("attempting", ins.describe()) # this will issue commands to the motion controller or change points

        self.currentInstruction = ins
        self.instructions.pop(0)

    def start(self, shouldStop):
        while not shouldStop.is_set():
            if len(self.instructions) < 3:
                self.instructions.append(self.instructionProvider.next())
            self._attemptNext()
            time.sleep(1.44321)

import time

class SectionInstruction():
    def __init__(self, name, dir):
        self.name = name
        self.direction = dir

    def describe(self):
        return "%s %s" % (self.name, self.direction)

class ShuttleOnSectionA():
    def __init__(self):
        self.isForwards = False

    def next(self):
        self.isForwards = not self.isForwards
        if self.isForwards:
            return SectionInstruction("A", "forwards")
        else:
            return SectionInstruction("A", "reverse")

class Detector():
    def state(self):
        return 0
        
class TimedSimulatingDetector():
    def __init__(self, t):
        self.dt = t
        self.last = time.time()

    def state(self):
        now = time.time()
        if (now - self.last) > self.dt:
            self.last = now
            return 1
        return 0

aStart = TimedSimulatingDetector(3)
aEnd = TimedSimulatingDetector(2)

layout = {
    "A": {
        "until": {
            "forwards": aStart,
            "reverse": aEnd
        }
    }
}

print("starting")
shuttle = ShuttleOnSectionA()
routingCtrl = RoutingController(shuttle, layout)

threadables = [
    Cmd(say),
    routingCtrl
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]
print("stopped")


