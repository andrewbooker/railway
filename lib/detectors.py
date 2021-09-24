
import time

#used in controller.py (ie not currently in use)
class Detector():
    def __init__(self, port, pos, callback):
        self.callback = callback
        self.pos = pos
        self.port = port
        self.state = 0

    def start(self, shouldStop):
        while not shouldStop.is_set():
            v = self.port.get()
            if v != self.state:
                self.callback(v, self.pos)
                self.state = v
            time.sleep(0.05)
