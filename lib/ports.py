
import RPi.GPIO as GPIO

class PwmPort():
    def __init__(self, port):
        GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(port, 100)
        self.pwm.start(0)

    def __del__(self):
        self.pwm.stop()

    def set(self, value):
        self.pwm.ChangeDutyCycle(value)

class Output():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, v):
        GPIO.output(self.port, v)
