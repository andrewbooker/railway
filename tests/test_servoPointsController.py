from application.servoPointsController import ServoPointsController
from lib.monitor import StatusComponent
from lib.ports import Ports


class LocalPort:
    def __init__(self):
        self.value = None

    def set(self, v):
        self.value = v


class LocalDevice(Ports):
    def servoPwmPort(self, p, initVal):
        return LocalPort()


class LocalStatus(StatusComponent):
    def __init__(self):
        StatusComponent.__init__(self, 99)
        self.msgs = []

    def setValue(self, v):
        self.msgs.append(v)


def test_can_set_points_left():
    device = LocalDevice()
    status = LocalStatus()
    ctrl = ServoPointsController(device, status)

    ctrl.set(8, "left")

    assert status.msgs == ["setting points 8 to left"]
    assert ctrl.points[8].val == 9
    assert ctrl.points[8].device.value == 9


def test_can_set_points_right():
    device = LocalDevice()
    status = LocalStatus()
    ctrl = ServoPointsController(device, status)

    ctrl.set(8, "right")

    assert status.msgs == ["setting points 8 to right"]
    assert ctrl.points[8].val == 6
    assert ctrl.points[8].device.value == 6
