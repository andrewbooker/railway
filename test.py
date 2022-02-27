#!/usr/bin/env python

from lib.rpiPorts import UsingRPi
from lib.arduinoPorts import UsingArduino
from lib.cmd import *
import RPi.GPIO as GPIO

import sys
port = int(sys.argv[1])
state = int(sys.argv[2])

#rpi = UsingRPi()
ard = UsingArduino()
ps = [ard.output(port)]

for p in ps:
    p.set(state)

def doNothing(t):
    pass
    
cmd = Cmd(doNothing)

threadables = [
    cmd
]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
[thread.start() for thread in threads]
[thread.join() for thread in threads]

#del rpi
print("stopped")

