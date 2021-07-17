#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import random


class Points():
    def __init__(self):
        servoPin = 14
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servoPin, GPIO.OUT)
        print("set up on pin", servoPin)

        self.p = GPIO.PWM(servoPin, 50)
        self.min = 6
        self.max = 9
        self.val = 0
        self.p.start(self.min)
        
    def __del__(self):
        self.p.stop()
        GPIO.cleanup()
        print("stopped")
        
    def _setTo(self, d, desc):
        if d == self.val:
            print("already at", desc)
            return
        self.p.ChangeDutyCycle(d)
        self.val = d
        print("set to", desc, self.val)
        
    def left(self):
        self._setTo(self.min, "left")
        
    def right(self):
        self._setTo(self.max, "right")

points = Points()

try:
    while True:
        time.sleep(3)
        points.left() if random.random() > 0.5 else points.right()

except KeyboardInterrupt:
  del points

