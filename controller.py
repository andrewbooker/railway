#!/usr/bin/env python

import sys
import math


class PowerMonitor():
    def __init__(self):
        self.scale = 100
        self.height = 3
        self.msg = ""
        self.firstValueWritten = False

    def setValue(self, value):
        bar = value
        fill = self.scale - bar

        if self.firstValueWritten:
            sys.stdout.write("\x1b[A" * (self.height + 1))
            sys.stdout.flush()
        else:
            self.firstValueWritten = True

        sys.stdout.write("%s%s\n\r" % (self.msg, " " * (self.scale - len(self.msg))))
        for h in range(self.height):
            sys.stdout.write("\033[92m%s\033[0m" % ("\u2589" * bar))
            sys.stdout.write("\033[0;37m%s\033[0m" % ("\u2589" * fill))
            sys.stdout.write("\n\r")

        sys.stdout.flush()

    def setMessage(self, m):
        self.msg = m


import time
import RPi.GPIO as GPIO

class Train():
    def __init__(self, port, monitor):
        self.monitor = monitor
        GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(port, 100)
        self.pwm.start(0)
        self.current = 0

    def __del__(self):
        self.pwm.stop()

    def _setTo(self, dc):
        self.pwm.ChangeDutyCycle(dc)
        self.current = dc
        self.monitor.setValue(dc)

    def rampTo(self, dc, timeInterval):
        if timeInterval == 0:
            self._setTo(dc)
            return

        ddc = abs(dc - self.current)
        secsPerIncr = 1.0 * timeInterval / ddc

        while not self.current == dc:
            incr = 1 if dc > self.current else -1
            self._setTo(self.current + incr)
            time.sleep(secsPerIncr)

class Direction():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, isForwards):
        GPIO.output(self.port, 0 if isForwards else 1)

portA = 12
portB = 18

GPIO.setmode(GPIO.BCM)

monitor = PowerMonitor()
train = Train(portA, monitor)
direction = Direction(23)

runsRemaining = 1
isForwards = False
direction.set(isForwards)
while runsRemaining > 0:
    monitor.setMessage("ramping up %s" % "forwards" if isForwards else "reverse")
    train.rampTo(60, 3)
    monitor.setMessage("holding steady")
    time.sleep(2)
    monitor.setMessage("ramping down")
    train.rampTo(0, 3)
    isForwards = not isForwards
    direction.set(isForwards)
    runsRemaining -= 1

print("stopped")

del train
GPIO.cleanup() 
