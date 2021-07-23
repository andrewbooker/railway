#!/usr/bin/env python

import time
import RPi.GPIO as GPIO

port = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
print("starting")
on = False
done = 0
while done < 10:
    setting = GPIO.HIGH if on else GPIO.LOW
    print("setting", setting)
    GPIO.output(port, setting)
    on = not on
    time.sleep(5)
    done += 1

GPIO.cleanup()
print("stopped")    
