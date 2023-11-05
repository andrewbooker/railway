#!/usr/bin/env python

import os

from application.directionRelays import DirectionRelays
from lib.monitor import PowerMonitor
from lib.speed import Speed
from application.commandBasedMotionController import CommandBasedMotionController
from lib.distribution import Direction
from lib.detectors import Detector
from lib.rpiPorts import UsingRPi
from lib.arduinoPorts import UsingArduino
os.system("clear")

portA = 12
portB = 18

rpi = UsingRPi()
ard = UsingArduino()

monitor = PowerMonitor()
speed = Speed(rpi.pwmPort(12), monitor)

def onPass(a, b):
    monitor.setMessage("points %s %s" % (a, b))

directionController = DirectionRelays(ard, monitor.msg)
directionController.portId = "arduino_41"
controller = CommandBasedMotionController(speed, monitor.msg, 90, directionController)

detectorA = Detector(rpi.input(14), "A", onPass)
detectorB = Detector(rpi.input(15), "B", onPass)

from lib.cmd import *
cmd = Cmd(controller.onCmd)

targets = [
    speed,
    detectorA,
    detectorB,
    cmd
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in targets]

[thread.start() for thread in threads]
[thread.join() for thread in threads]


del rpi
