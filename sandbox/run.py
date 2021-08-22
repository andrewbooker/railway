#!/usr/bin/env python

import sys
import threading


class RoutingController():
    def __init__(self, instructionProvider, layout, monitor):
        self.monitor = monitor
        self.instructions = []
        self.currentInstruction = None
        self.layout = layout
        self.instructionProvider = instructionProvider

    def next(self):
        if len(self.instructions) < 3:
            self.instructions.append(self.instructionProvider.next())

        ins = self.instructions[0]
        section = self.layout["sections"][ins.name]
        if self.currentInstruction is not None:
            if "until" in section:
                until = section["until"]
                if ins.direction not in until or until[ins.direction].state() == 0:
                    return
                else:
                    self.instructions.pop(0)
        
        if ins != self.currentInstruction:
            self.monitor.setMessage("attempting %s" % ins.describe())
            direction = section["direction"]
            isForwards = "f" in ins.cmds[0]
            direction.set(isForwards)
        
        self.currentInstruction = ins

import time
class ControlLoop():
    def __init__(self, c, i):
        self.c = c
        self.i = i

    def start(self, shouldStop):
        while not shouldStop.is_set():
            self.c.next()
            time.sleep(self.i)



class SectionInstruction():
    def __init__(self, name, cmds):
        self.name = name
        self.cmds = cmds
        self.direction = "forwards" if "f" in cmds[0] else "reverse"

    def describe(self):
        return "%s %s" % (self.name, self.cmds)

class ShuttleOnSectionA():
    def __init__(self):
        self.isForwards = False

    def next(self):
        self.isForwards = not self.isForwards
        if self.isForwards:
            return SectionInstruction("A", ["f", "s"])
        else:
            return SectionInstruction("A", ["r", "s"])

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

import os
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()
sys.path.append(parentDir)
from lib.navigator import Journey


#from lib.monitor import PowerMonitor
#from lib.rpiPorts import PwmPort, Output, UsingRPi
from lib.speed import MotionController, Speed
from lib.distribution import Direction
from lib.stdump import PowerMonitor, PwmPort, Output
from lib.cmd import Cmd, shouldStop

#ports = UsingRPi()
monitor = PowerMonitor()
speed = Speed(PwmPort(12), monitor)
directionOf = {"A": Direction(Output(23))}
controller = MotionController(speed, directionOf, monitor, 8, "A")
cmd = Cmd(controller.onCmd)

endToEnd = {
    "sections": {
        "A": {
            "direction": directionOf["A"],
            "until": {
                "forwards": aEnd,
                "reverse": aStart
            }
        }
    }
}

loop = {
    "sections": {"A": { "direction": directionOf["A"] } }
}

print("starting")

instructionProvider = ShuttleOnSectionA()
routingCtrl = RoutingController(instructionProvider, loop, monitor)
controlLoop = ControlLoop(routingCtrl, 1.3422)


threadables = [
    cmd,
    speed,
    controlLoop
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

#del ports
print("stopped")

