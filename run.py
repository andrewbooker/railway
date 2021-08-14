#!/usr/bin/env python

from lib.cmd import *
import sys
import threading


def say(what):
    sys.stdout.write("%s\r\n" % what)


class RoutingController():
    def __init__(self):
        self.instructions = []
        self.lock = threading.Lock()
        self.checkpoints = {}
        self.sections = {}
        self.points = {}

    def _attemptNext(self):
        if self.lock.locked() or len(self.instructions) == 0:
            return

        ins = self.instructions[0]
        print("attempting", ins.describe())

        self.instructions.pop(0)

    def instruct(self, instruction):
        self.lock.acquire()
        self.instructions.append(instruction)
        self.lock.release()

    def isReady(self):
        return len(self.instructions) < 3

    def start(self, shouldStop):
        while not shouldStop.is_set():
            self._attemptNext()
            time.sleep(1.44321)

import time
class Instructor():
    def __init__(self, routingCtrl):
        self.ctrl = routingCtrl

    def next(self):
        pass

    def start(self, shouldStop):
        while not shouldStop.is_set():
            if self.ctrl.isReady():
                ins = self.next()
                say(ins.describe())
                self.ctrl.instruct(ins)
            time.sleep(1.0)


class SectionInstruction():
    def __init__(self, name, dir):
        self.name = name
        self.section = dir

    def describe(self):
        return "%s %s" % (self.name, self.section)

class ShuttleOnSectionA(Instructor):
    def __init__(self, ctrl):
        super().__init__(ctrl)
        self.isForwards = False

    def next(self):
        self.isForwards = not self.isForwards
        if self.isForwards:
            return SectionInstruction("A", "forwards")
        else:
            return SectionInstruction("A", "reverse")



print("starting")
routingCtrl = RoutingController()
shuttle = ShuttleOnSectionA(routingCtrl)

threadables = [
    Cmd(say),
    routingCtrl,
    shuttle
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]
print("stopped")


