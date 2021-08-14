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
        self.checkpoints = {}
        self.sections = {}
        self.points = {}

    def _attemptNext(self):
        if len(self.instructions) == 0:
            return

        ins = self.instructions[0]
        sectionLayout = self.layout[ins.name] # so far only have section instructions
        if self.currentInstruction is not None:                
            until = sectionLayout["until"]
            if until is None or until[ins.direction] is None or until[ins.direction].state() == 0:
                return
        
        ctrl = sectionLayout["power"]
        if ctrl is not None:
            self.monitor.setMessage("attempting %s" % ins.describe()) # this will issue commands to the motion controller or change points
            # usually no ramping here. simply apply the A or B power in the direction 
            # only ramp down/up if entering/leaving a siding
            # ramps for manual stops or manual direction changes are handled in the MotionController commands
        
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


#from lib.monitor import PowerMonitor
#from lib.rpiPorts import PwmPort, Output, UsingRPi
from lib.speed import MotionController, Speed
from lib.distribution import Direction
from lib.stdump import PowerMonitor, PwmPort, Output
from lib.cmd import Cmd, shouldStop

#ports = UsingRPi()
monitor = PowerMonitor()
speed = Speed(PwmPort(12), monitor)
direction = Direction(Output(23))
controller = MotionController(speed, direction, monitor)
cmd = Cmd(controller.onCmd)

layout = {
    "A": {
        "power": controller,
        "until": {
            "forwards": aStart,
            "reverse": aEnd
        }
    }
}

print("starting")

shuttle = ShuttleOnSectionA()
routingCtrl = RoutingController(shuttle, layout, monitor)

threadables = [
    cmd,
    routingCtrl,
    speed
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

#del ports
print("stopped")


