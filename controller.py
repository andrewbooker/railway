#!/usr/bin/env python

import sys
import math
import os
import threading
os.system("clear")
print("")

class PowerMonitor():
    def __init__(self):
        self.scale = 100
        self.height = 3
        self.msg = ""
        self.bar = 0
        self.firstValueWritten = False
        self.lock = threading.Lock()

    def _render(self):
        if self.lock.locked():
            return
        self.lock.acquire()
        fill = self.scale - self.bar

        if self.firstValueWritten:
            sys.stdout.write("\x1b[A" * (self.height + 1))
            sys.stdout.flush()
        else:
            self.firstValueWritten = True

        sys.stdout.write("%s%s\n\r" % (self.msg, " " * (self.scale - len(self.msg))))
        for h in range(self.height):
            sys.stdout.write("\033[92m%s\033[0m" % ("\u2589" * self.bar))
            sys.stdout.write("\033[0;37m%s\033[0m" % ("\u2589" * fill))
            sys.stdout.write("\n\r")

        sys.stdout.flush()
        self.lock.release()

    def setValue(self, value):
        self.bar = value
        self._render()

    def setMessage(self, m):
        self.msg = m
        self._render()


import time
import RPi.GPIO as GPIO


class Direction():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, isForwards):
        GPIO.output(self.port, 0 if isForwards else 1)



class Detector():
    def __init__(self, port, pos, callback):
        self.callback = callback
        self.pos = pos
        self.port = port
        self.state = 0
        GPIO.setup(self.port, GPIO.IN)

    def start(self, shouldStop):
        while not shouldStop.is_set():
            v = GPIO.input(self.port)
            if v != self.state:
                self.callback(v, self.pos)
                self.state = v
            time.sleep(0.05)


class ServoPort(): # should contain a pwm port
    def __init__(self, port):
        GPIO.setup(port, GPIO.OUT)

        self.p = GPIO.PWM(port, 50)

    def __del__(self, port):
        self.p.stop()

    def setLeft(self):
        pass

    def setRight(self):
        pass

class Points():
    def __init__(self, port):
        self.port = port

    def set(self, selection):
        pass

class Section():
    def __init__(self, port):
        self.port = port

    def __del__(self):
        del self.port

    def power(self, direction):
        pass

portA = 12
portB = 18

GPIO.setmode(GPIO.BCM)

monitor = PowerMonitor()

from lib.speed import MotionController, Speed
from lib.ports import PwmPort
speed = Speed(PwmPort(portA), monitor)
direction = Direction(23)

controller = MotionController(speed, direction, monitor)
detectorA = Detector(14, "A", controller.onPass)
detectorB = Detector(15, "B", controller.onPass)

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

del speed
GPIO.cleanup()
