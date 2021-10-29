#!/usr/bin/env python

import time
import threading
import readchar
import sys
import os
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()

sys.path.append(parentDir)
from lib.arduinoPorts import UsingArduino


def stdout(s):
    sys.stdout.write("%s\n\r" % s)


def detect(shouldStop, ua, pin):
    inP = ua.input(pin)

    stdout("read started on %d" % pin)
    inState = 0
    while not shouldStop.is_set():
        d = inP.get()
        if d is not inState:
            stdout("%d in state %d" % (pin, 0 if d != 1 else d))
            inState = d

        time.sleep(0.05)
    stdout("stopping read on %d" % pin)

def blink(shouldStop, ua, pin):
    outPin = ua.output(pin)
    state = 0
    while not shouldStop.is_set():
        outPin.set(state)
        state = 1 if state == 0 else 0
        time.sleep(0.5)
    stdout("stopping blink on %d" % pin)

def servo(shouldStop, ua, pin):
    p = ua.servoPwmPort(pin, 10)
    state = 0
    while not shouldStop.is_set():
        v = 70 if state == 0 else 20
        stdout("servo %d" % v)
        p.set(v)
        state = 1 if state == 0 else 0
        time.sleep(1.6)
    stdout("stopping servo on %d" % pin)


ua = UsingArduino()
shouldStop = threading.Event()
threads = []
threads.append(threading.Thread(target=detect, args=(shouldStop, ua, 52), daemon=True))
threads.append(threading.Thread(target=detect, args=(shouldStop, ua, 53), daemon=True))
#threads.append(threading.Thread(target=blink, args=(shouldStop, ua, 5), daemon=True))
#threads.append(threading.Thread(target=servo, args=(shouldStop, ua, 6), daemon=True))
print("Started (press 'q' to stop)")
[t.start() for t in threads]

while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()

[t.join() for t in threads]
del(ua)
