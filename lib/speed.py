
import time

class MotionController():
    def __init__(self, speed, sectionDirections, monitor, maxSpeed, startingSection):
    # note the monitor is currently a train speed indicator, yet the direction notifications will be a section-specific sequence
        self.maxSpeed = maxSpeed
        self.speed = speed
        self.directionOf = sectionDirections
        self.monitor = monitor
        self.isRunning = False
        self.isStopping = False
        self.isForwards = True
        self.commandsBlocked = False
        self.monitor.setMessage("set to %s" % ("forwards" if self.isForwards else "reverse"))
        self.currentSection = startingSection

    def _start(self):
        d = "forwards" if self.isForwards else "reverse"
        self.monitor.setMessage("ramping up %s %s" % (self.currentSection, d))
        self.directionOf[self.currentSection].set(self.isForwards)
        self.isRunning = True
        self.speed.rampTo(self.maxSpeed, lambda: self.monitor.setMessage("holding steady"))

    def _setStopped(self):
        self.isRunning = False
        self.isStopping = False
        self.commandsBlocked = False
        self.monitor.setMessage("stopped")

    def _stop(self):
        if not self.isRunning:
            return
        self.isStopping = True
        self.monitor.setMessage("ramping down")
        self.speed.rampTo(0, self._setStopped)
        while self.isRunning:
            time.sleep(0.05)

    def _hardStop(self):
        self.speed._setTo(0)
        self._setStopped()
        self.commandsBlocked = True

    def _changeDirection(self):
        wasRunning = self.isRunning
        if self.isRunning and not self.isStopping:
            self._stop()

        self.isForwards = not self.isForwards
        self.monitor.setMessage("changing to %s" % ("forwards" if self.isForwards else "reverse"))

        if wasRunning:
            self._start()

    def setCurrentSection(self, s):
        self.currentSection = s

    def onPass(self, pos, sectionName):
        if self.isStopping or self.commandsBlocked:
            return

        self.commandsBlocked = True
        self.monitor.setMessage("passed checkpoint %s on %s" % (pos, sectionName))
        self._hardStop()
        self._changeDirection()
        self._start()
        self.commandsBlocked = False

    def onCmd(self, c):
        if self.commandsBlocked:
            self.monitor.setMessage("Command blocked after checkpoint")
            return

        if c in ['s', ' ']:
            if not self.isRunning:
                self._start()
            else:
                self._stop()

        if c == 'd' or (c == 'r' and self.isForwards) or (c == 'f' and not self.isForwards):
            self._changeDirection()

        if c == '+':
            self.isRunning = True
            if self.speed.target < 100:
                self.speed.target += 1

        if c == '-':
            if self.speed.target > 0:
                self.speed.target -= 1
            else:
                self.isRunning = False

class Speed():
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

    def _setTo(self, dc):
        self.port.set(dc)
        self.current = dc
        self.monitor.setValue(dc)

    def rampTo(self, dc, onDone):
        self.onDone = onDone
        self.target = max(min(dc, 100), 0)

    def start(self, shouldStop):
        while not shouldStop.is_set():
            if self.target < self.current:
                self._setTo(self.current - 1)
            elif self.target > self.current:
                self._setTo(self.current + 1)
            elif self.onDone is not None:
                self.onDone()
                self.onDone = None

            time.sleep(self.secsPerIncr)
        if shouldStop.is_set():
            self._setTo(0)
