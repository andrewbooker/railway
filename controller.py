#!/usr/bin/env python

import time
import RPi.GPIO as GPIO

port = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
pwm = GPIO.PWM(port, 100)


pwm.start(0)

dc = 0
done = False
print("ramping up")
while not done:
    dc += 1
    pwm.ChangeDutyCycle(dc)
    if (dc == 100):
        done = True
    time.sleep(0.1)

print("holding steady")
time.sleep(5)

done = False
print("ramping down")
while not done:
    dc -= 1
    pwm.ChangeDutyCycle(dc)
    if (dc == 0):
        done = True

    time.sleep(0.1)

print("stopped")
pwm.stop()
GPIO.cleanup() 
