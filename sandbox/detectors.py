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


def say(txt):
    sys.stdout.write(f"{txt}\r\n")
    sys.stdout.flush()


class Detector:
    def __init__(self, port, pos, callback):
        self.callback = callback
        self.pos = pos
        self.port = port
        self.state = None

    def start(self, shouldStop):
        while not shouldStop.is_set():
            v = self.port.get()
            if v != self.state:
                self.callback(v, self.pos)
                self.state = v
            time.sleep(0.05)

def doNothing(t):
    pass


rpi = UsingRPi()
threadables = [Cmd(doNothing)]

for p in [8, 14, 15, 21, 24]:
    say(f"registering RPi port {p}")
    threadables.append(Detector(rpi.input(p), f"port {p}", lambda a, b: say(f"{a} {b}")))

threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in threadables]
say("starting")
[thread.start() for thread in threads]
say("started")
[thread.join() for thread in threads]
say("stopped")
