import time

from lib.routeNavigator import MotionController
from lib.directionController import DirectionController, Direction


class CommandBasedMotionController(MotionController):
    def __init__(self, speed, statusComponent, maxSpeed, directionController: DirectionController):
        self.maxSpeed = maxSpeed
        self.speed = speed
        self.directionController = directionController
        self.statusComponent = statusComponent
        self.isRunning = False
        self.isStopping = False
        self.direction = Direction.Forward
        self.commandsBlocked = False
        self.changeDirectionCallback = None

    def withChangeDirectionCallback(self, cb):
        self.changeDirectionCallback = cb
        return self

    def _start(self):
        self.directionController.set(self.directionController.currentPortId(), self.direction)
        self.isRunning = True
        self.statusComponent.setValue(f"ramping up to {self.maxSpeed}")
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

        self.direction = self.direction.opposite()
        self.statusComponent.setValue(f"changing to {self.direction.value}")
        if self.changeDirectionCallback is not None:
            self.changeDirectionCallback(self.directionController.currentPortId())

        if wasRunning:
            self._start()

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

        if c == 'd' or (c == 'r' and self.direction == Direction.Forward) or (c == 'f' and self.direction == Direction.Reverse):
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
