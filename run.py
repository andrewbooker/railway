#!/usr/bin/env python

import sys
import os
import random
from lib.routeIterator import RouteIterator, PointsSelector
from lib.routeNavigator import *
from lib.detectionRouter import DetectionRouter
from lib.speed import Speed
from lib.monitor import PowerMonitor
from lib.cmd import *
from application.trafficListener import TrafficListener
from application.directionRelays import DirectionRelays
from application.servoPointsController import ServoPointsController
from application.commandBasedMotionController import CommandBasedMotionController
from lib.arduinoPorts import UsingArduino
from lib.model import Model
from lib.rpiPorts import UsingRPi, ServoPwmPort

layoutStr = None
if len(sys.argv) < 2:
    print("specify layout json file")
    exit()
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

startingSectionId = sys.argv[2] if len(sys.argv) > 2 else None

os.system("clear")
rpi = UsingRPi()
ard = UsingArduino()
monitor = PowerMonitor()
pointsController = ServoPointsController(rpi, monitor.msg)
detectionRouter = DetectionRouter(monitor.msg)
detectionListener = TrafficListener(detectionRouter)

class RandomPointsSelector(PointsSelector):
    def __init__(self, status):
        self.status = status

    def select(self):
        s = "left" if 0 != (int(random.random() * 10) % 2) else "right"
        self.status.setValue(f"selecting {s}")
        return s

model = Model(layoutStr)
detectionListener.registerInputDevices("arduino", ard)
detectionListener.registerInputDevices("RPi", rpi)
modelDetectors = model.detectionPorts()
for bank in modelDetectors:
    detectionListener.registerPorts(bank, modelDetectors[bank])

speed = Speed(rpi.pwmPort(12), monitor)

directionRelays = DirectionRelays(ard, monitor.msg)
controlLoop = ControlLoop(detectionListener.poll, 0.1)
controller = CommandBasedMotionController(speed, monitor.msg, 90, directionRelays)
navigator = RouteNavigator(model, directionRelays, detectionRouter, pointsController, controller)
iterator = RouteIterator(model, navigator, RandomPointsSelector(monitor.msg))
detectionRouter.setCallback(iterator.next)

if startingSectionId is not None:
    iterator.startAtSection(startingSectionId)
    monitor.msg.setValue(f"starting at {iterator.current[0]}")
else:
    monitor.msg.setValue("starting")

iterator.next()

def localCommandHandler(c):
    if c == 'c':
        iterator.next()
    controller.onCmd(c)

cmd = Cmd(localCommandHandler)
threadables = [
    speed,
    cmd,
    controlLoop
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

del ard
del rpi
monitor.msg.setValue("stopped")
