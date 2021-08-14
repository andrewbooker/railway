
import sys

class Dump():
    def write(self, what):
        sys.stdout.write("%s\r\n" % what)
        sys.stdout.flush()

class PowerMonitor(Dump):
    def __init__(self):
        self.lastW = 0

    def setValue(self, v):
        if (self.lastW % 100) == 0:
            pass            
            #self.write("value: %s" % v)
        self.lastW += 1

    def setMessage(self, m):
        self.write("msg: %s" % m)

class Port(Dump):
    def __init__(self, n, label):
        self.n = n
        self.label = label

    def set(self, v):
        self.write("%s value to %d: %s" % (self.label, self.n, v))

class PwmPort(Port):
    def __init__(self, n):
        super().__init__(n, "pwm")

class Output(Port):    
    def __init__(self, n):
        super().__init__(n, "basic")

