#!/usr/bin/env python

from lib.cmd import *
import sys
import threading


def say(what):
    sys.stdout.write("%s\r\n" % what)


class RoutingController():
    def __init__(self, instructionProvider):
        self.instructions = []
        self.instructionProvider = instructionProvider
        self.checkpoints = {}
        self.sections = {}
        self.points = {}

    def _attemptNext(self):
        if len(self.instructions) == 0:
            return

        ins = self.instructions[0]
        print("attempting", ins.describe())

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
        self.section = dir

    def describe(self):
        return "%s %s" % (self.name, self.section)

class ShuttleOnSectionA():
    def __init__(self):
        self.isForwards = False

    def next(self):
        self.isForwards = not self.isForwards
        if self.isForwards:
            return SectionInstruction("A", "forwards")
        else:
            return SectionInstruction("A", "reverse")



print("starting")
shuttle = ShuttleOnSectionA()
routingCtrl = RoutingController(shuttle)

threadables = [
    Cmd(say),
    routingCtrl
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]
print("stopped")


