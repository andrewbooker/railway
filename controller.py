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

portA = 12
portB = 18
port = portA

GPIO.setmode(GPIO.BCM)
GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
pwm = GPIO.PWM(port, 100)


monitor = PowerMonitor()
pwm.start(0)

dc = 0
done = False
monitor.setMessage("ramping up")
while not done:
    dc += 1
    pwm.ChangeDutyCycle(dc)
    monitor.setValue(dc)
    if (dc == 100):
        done = True
    time.sleep(0.1)


monitor.setMessage("holding steady")
monitor.setValue(dc)
time.sleep(5)

done = False
monitor.setMessage("ramping down")
while not done:
    dc -= 1
    pwm.ChangeDutyCycle(dc)
    monitor.setValue(dc)
    if (dc == 0):
        done = True

    time.sleep(0.1)

print("stopped")
pwm.stop()
GPIO.cleanup() 
