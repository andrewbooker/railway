#!/usr/bin/env python

import os
import sys
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()
sys.path.append(parentDir)
from lib.rpiPorts import UsingRPi
from lib.cmd import *
from lib.detectors import Detector
from lib.stdump import Dump
import RPi.GPIO as GPIO

possiblePorts = [
    8, 14, 15, 23, 24, 25
]

rpi = UsingRPi()
def doNothing(t):
    pass

cmd = Cmd(doNothing)

threadables = [
    cmd
]


def onPass(a, b):
    Dump().write("%s %s" % (a, b))

for p in possiblePorts:
    threadables.append(Detector(rpi.input(p), "port %d" % p, onPass))

threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

print("stopped")
