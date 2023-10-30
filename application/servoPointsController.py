from lib.hardwarePoints import HardwarePoints
from lib.monitor import StatusComponent
from lib.ports import Ports
from lib.routeNavigator import PointsController


class ServoPointsController(PointsController):
    def __init__(self, ports: Ports, status: StatusComponent):
        self.ports = ports
        self.status = status

    def set(self, port, s):
        self.status.setValue(f"setting points {port} to {s}")
        points = HardwarePoints(self.ports.servoPwmPort(port, HardwarePoints.LEFT))
        if s == "left":
            points.left()
        if s == "right":
            points.right()
