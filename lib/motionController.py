import time


class MotionController:
    def __init__(self, speed, sectionDirections, statusComponent, maxSpeed, startingSection):
        self.maxSpeed = maxSpeed
        self.speed = speed
        self.directionOf = sectionDirections
        self.statusComponent = statusComponent
        self.isRunning = False
        self.isStopping = False
        self.isForwards = True
        self.commandsBlocked = False
        self.currentSection = startingSection
        self.statusComponent.setValue("set %s to %s" % (self.currentSection, "forwards" if self.isForwards else "reverse"))
        self.changeDirectionCallback = None

    def withChangeDirectionCallback(self, cb):
        self.changeDirectionCallback = cb
        return self

    def _start(self):
        d = "forwards" if self.isForwards else "reverse"
        self.statusComponent.setValue("ramping %s up to %s" % (self.currentSection, d))
        self.directionOf[self.currentSection].set(self.isForwards)
        self.isRunning = True
        self.speed.rampTo(self.maxSpeed, lambda: self.statusComponent.setValue("holding steady"))

    def _setStopped(self):
        self.isRunning = False
        self.isStopping = False
        self.commandsBlocked = False
        self.statusComponent.setValue("stopped")

    def _stop(self):
        if not self.isRunning:
            return
        self.isStopping = True
        self.statusComponent.setValue("ramping down")
        self.speed.rampTo(0, self._setStopped)
        while self.isRunning:
            time.sleep(0.05)

    def _hardStop(self):
        self.speed.setTo(0)
        self._setStopped()
        self.commandsBlocked = True

    def _changeDirection(self):
        wasRunning = self.isRunning
        if self.isRunning and not self.isStopping:
            self._stop()

        self.isForwards = not self.isForwards
        self.statusComponent.setValue("changing %s to %s" % (self.currentSection, "forwards" if self.isForwards else "reverse"))
        if self.changeDirectionCallback is not None:
            self.changeDirectionCallback({"id": self.currentSection})

        if wasRunning:
            self._start()

    def setCurrentSection(self, s):
        self.currentSection = s

    def onCheckpoint(self):
        if self.isStopping or self.commandsBlocked:
            return

        self.commandsBlocked = True
        self.statusComponent.setValue("hit checkpoint")
        self._hardStop()
        self._changeDirection()
        self._start()
        self.commandsBlocked = False

    def onCmd(self, c):
        if self.commandsBlocked:
            self.statusComponent.setValue("Command blocked after checkpoint")
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
