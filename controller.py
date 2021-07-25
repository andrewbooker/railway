#!/usr/bin/env python

import sys
import math


class PowerMonitor():
    def __init__(self):
        self.scale = 100
        self.height = 3
        self.msg = ""
        self.bar = 0
        self.firstValueWritten = False

    def _render(self):
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

    def setValue(self, value):
        self.bar = value
        self._render()

    def setMessage(self, m):
        self.msg = m
        self._render()


import time
import RPi.GPIO as GPIO

class Speed():
    def __init__(self, port, monitor, shouldStop):
        self.shouldStop = shouldStop
        self.monitor = monitor
        GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(port, 100)
        self.pwm.start(0)
        self.current = 0
        self.monitor.setValue(0)

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

        while not self.current == dc and not self.shouldStop.is_set():
            incr = 1 if dc > self.current else -1
            self._setTo(self.current + incr)
            time.sleep(secsPerIncr)
        if self.shouldStop.is_set():
            self._setTo(0)

class Direction():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, isForwards):
        GPIO.output(self.port, 0 if isForwards else 1)

class Controller():
    def __init__(self, speed, direction, monitor):
        self.speed = speed
        self.direction = direction
        self.monitor = monitor
        self.isRunning = False
        self.isForwards = True
        self.monitor.setMessage("set to %s" % ("forwards" if self.isForwards else "reverse"))

    def _start(self):
        self.monitor.setMessage("ramping up %s" % ("forwards" if self.isForwards else "reverse"))
        self.direction.set(self.isForwards)
        self.isRunning = True
        self.speed.rampTo(65, 3)
        self.monitor.setMessage("holding steady")

    def _stop(self):
        if not self.isRunning:
            return
        self.monitor.setMessage("ramping down")
        self.speed.rampTo(0, 3)
        self.isRunning = False

    def onCmd(self, c):
        if c in [ord("s"), ord(" ")]:
            if not self.isRunning:
                self._start()
            else:
                self._stop()

        if c in [ord("d")]:
            wasRunning = self.isRunning
            if self.isRunning:
                self._stop()

            self.isForwards = not self.isForwards
            self.monitor.setMessage("changing to %s" % ("forwards" if self.isForwards else "reverse"))

            if wasRunning:
                self._start()


import readchar

class Cmd():
    def __init__(self, callback):
        self.callback = callback

    def start(self, shouldStop):
        while not shouldStop.is_set():
            c = ord(readchar.readchar())
            if c in [3, 27, 113]:
                shouldStop.set()
            else:
                self.callback(c)

import threading
shouldStop = threading.Event()

portA = 12
portB = 18

GPIO.setmode(GPIO.BCM)

monitor = PowerMonitor()
speed = Speed(portA, monitor, shouldStop)
direction = Direction(23)
controller = Controller(speed, direction, monitor)
cmd = Cmd(controller.onCmd)
thread = threading.Thread(target=cmd.start, args=(shouldStop,), daemon=True)
thread.start()
thread.join()

del speed
GPIO.cleanup() 
