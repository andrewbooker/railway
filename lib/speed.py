import time


class Speed:
    def __init__(self, port, monitor):
        self.monitor = monitor
        self.port = port
        self.current = 0
        self.target = 0
        self.secsPerIncr = 3.0 / 50
        self.monitor.setValue(0)
        self.onDone = None

    def __del__(self):
        del self.port

    def setTo(self, dc):
        self.port.set(dc)
        self.current = dc
        self.monitor.setValue(dc)

    def rampTo(self, dc, onDone):
        self.onDone = onDone
        self.target = max(min(dc, 100), 0)

    def start(self, shouldStop):
        while not shouldStop.is_set():
            if self.target < self.current:
                self.setTo(self.current - 1)
            elif self.target > self.current:
                self.setTo(self.current + 1)
            elif self.onDone is not None:
                self.onDone()
                self.onDone = None

            time.sleep(self.secsPerIncr)
        if shouldStop.is_set():
            self.setTo(0)
