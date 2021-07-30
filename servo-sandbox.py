#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import random

class Points():
    def __init__(self, servoPin):
        GPIO.setup(servoPin, GPIO.OUT)

        self.p = GPIO.PWM(servoPin, 50)
        self.r = 6
        self.l = 9

        self.val = self.r
        self.p.start(self.r)
        
    def __del__(self):
        self.p.stop()

    def _setTo(self, d, desc):
        if d == self.val:
            return
        self.p.ChangeDutyCycle(d)
        self.val = d
        print("set to", desc)
        
    def left(self):
        self._setTo(self.l, "left")
        
    def right(self):
        self._setTo(self.r, "right")


GPIO.setmode(GPIO.BCM)
points = Points(23)


try:
    while True:
        time.sleep(3)
        points.left() if random.random() > 0.5 else points.right()

except KeyboardInterrupt:
  del points

GPIO.cleanup()
