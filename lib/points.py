
import RPi.GPIO as GPIO

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

