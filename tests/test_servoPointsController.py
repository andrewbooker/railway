from application.servoPointsController import ServoPointsController
from lib.monitor import StatusComponent
from lib.ports import Ports
from lib.hardwarePoints import HardwarePoints


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

    ctrl.set("device_8", "left")

    assert status.msgs == ["setting points device_8 to left", "registering points at device_8"]
    assert ctrl.points["device_8"].val == HardwarePoints.LEFT
    assert ctrl.points["device_8"].device.value == HardwarePoints.LEFT


def test_can_set_points_right():
    device = LocalDevice()
    status = LocalStatus()
    ctrl = ServoPointsController(device, status)

    ctrl.set("device_8", "right")

    assert status.msgs == ["setting points device_8 to right", "registering points at device_8"]
    assert ctrl.points["device_8"].val == HardwarePoints.RIGHT
    assert ctrl.points["device_8"].device.value == HardwarePoints.RIGHT
