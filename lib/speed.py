
import time

class MotionController():
    def __init__(self, speed, direction, monitor):
    # note the monitor is currently a train speed indicator, yet the direction notifications will be a section-specific sequence
        self.maxSpeed = 70
        self.speed = speed
        self.direction = direction
        self.monitor = monitor
        self.isRunning = False
        self.isStopping = False
        self.isForwards = True
        self.commandsBlocked = False
        self.monitor.setMessage("set to %s" % ("forwards" if self.isForwards else "reverse"))

    def _start(self):
        self.monitor.setMessage("ramping up %s" % ("forwards" if self.isForwards else "reverse"))
        self.direction.set(self.isForwards)
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

    def _changeDirection(self):
        wasRunning = self.isRunning
        if self.isRunning and not self.isStopping:
            self._stop()

        self.isForwards = not self.isForwards
        self.monitor.setMessage("changing to %s" % ("forwards" if self.isForwards else "reverse"))

        if wasRunning:
            self._start()

#remove this and have something layout-aware pass 's' or 'd' commands
    def onPass(self, v, pos):
        return
        if self.isStopping or not v:
            return

        self.monitor.setMessage("passed checkpoint %s" % pos)
        if (pos in ["A"] and self.isForwards) or (pos in ["B"] and not self.isForwards):
            self.commandsBlocked = True
            self._changeDirection()

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
            self.speed.target += 1

        if c == '-':
            self.speed.target -= 1
