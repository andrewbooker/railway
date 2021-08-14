
import RPi.GPIO as GPIO

class Direction():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, isForwards):
        GPIO.output(self.port, 0 if isForwards else 1)
