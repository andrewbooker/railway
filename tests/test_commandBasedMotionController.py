from application.commandBasedMotionController import CommandBasedMotionController
from lib.directionController import DirectionController, Direction


class Callback:
    def __init__(self):
        self.with_id = 0

    def cb(self, i):
        self.with_id = i


class LocalSpeed:
    def __init__(self):
        self.speed = 0

    def rampTo(self, s, onDone):
        self.speed = s
        onDone()


class LocalStatusComponent:
    def __init__(self):
        self.status = []

    def setValue(self, s):
        self.status.append(s)


def test_is_initially_at_standstill():
    controller = CommandBasedMotionController(None, None, 99, None)

    assert controller.isRunning is False
    assert controller.isStopping is False
    assert controller.isForwards is True
    assert controller.commandsBlocked is False


def test_starts_motion_from_standstill():
    direction_controller = DirectionController()
    speed = LocalSpeed()
    status = LocalStatusComponent()
    controller = CommandBasedMotionController(speed, status, 87, direction_controller)

    controller.onCmd(' ')
    assert controller.isRunning is True
    assert speed.speed == 87
    assert status.status == ["ramping up to 87", "holding steady"]
    assert direction_controller.direction == Direction.Forward
    assert controller.isStopping is False
    assert controller.isForwards is True
    assert controller.commandsBlocked is False


def test_can_set_motion_in_reverse_before_starting():
    callback = Callback()
    direction_controller = DirectionController()
    speed = LocalSpeed()
    status = LocalStatusComponent()
    direction_controller.portId = "thing_0"
    controller = CommandBasedMotionController(speed, status, 99, direction_controller).withChangeDirectionCallback(callback.cb)

    controller.onCmd('d')
    assert controller.isForwards is False
    assert callback.with_id == "thing_0"
    assert status.status == ["changing thing_0 to reverse"]

    # was not running
    assert direction_controller.direction is None
    assert speed.speed == 0
    assert controller.isRunning is False
    assert controller.isStopping is False
