
import readchar
import threading

class Cmd():
    def __init__(self, callback):
        self.callback = callback

    def start(self, shouldStop):
        while not shouldStop.is_set():
            c = readchar.readchar()
            if ord(c) in [3, 27, 113]: #ctrl+C, esc or q
                shouldStop.set()
            else:
                self.callback(c)

import time
class ControlLoop():
    def __init__(self, c, i):
        self.c = c
        self.i = i

    def start(self, shouldStop):
        passed = 0
        dt = 0.05
        while not shouldStop.is_set():
            if passed > self.i:
                self.c()
                passed = 0
            time.sleep(dt)
            passed += dt

shouldStop = threading.Event()
