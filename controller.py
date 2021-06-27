#!/usr/bin/env python

import time
import RPi.GPIO as GPIO

port = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
pwm = GPIO.PWM(port, 100)


pwm.start(0)


try:
  print("started")
  while True:
    for dc in range(0, 100):
      pwm.ChangeDutyCycle(dc)
      time.sleep(0.02)
    for dc in range(99, 0, -1):
      pwm.ChangeDutyCycle(dc)
      time.sleep(0.02)
except KeyboardInterrupt:
  print("stopped")

pwm.stop()
GPIO.cleanup() 
