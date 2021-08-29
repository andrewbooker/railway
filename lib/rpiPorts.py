
import RPi.GPIO as GPIO

class PwmPort():
    def __init__(self, port, f=100, initVal=0):
        GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(port, f)
        self.pwm.start(initVal)

    def __del__(self):
        self.pwm.stop()

    def set(self, value):
        self.pwm.ChangeDutyCycle(value)

class ServoPwmPort(PwmPort):
    def __init__(self, port, initVal):
        super().__init__(port, 50, initVal)

class Input():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.IN)

    def get(self):
        return GPIO.input(self.port)

class Output():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, v):
        GPIO.output(self.port, v)

class UsingRPi():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.devices = []

    def __del__(self):
        for d in self.devices:
            del d
        GPIO.cleanup()

    def _add(self, d):
        self.devices.append(d)
        return d

    def input(self, port):
        return self._add(Input(port))

    def output(self, port):
        return self._add(Output(port))

    def pwmPort(self, port):
        return self._add(PwmPort(port))

    def servoPwmPort(self, port, initVal):
        return self._add(ServoPwmPort(port, initVal))
