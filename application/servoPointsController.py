from lib.hardwarePoints import HardwarePoints
from lib.monitor import StatusComponent
from lib.ports import Ports
from lib.routeNavigator import PointsController


class ServoPointsController(PointsController):
    def __init__(self, ports: Ports, status: StatusComponent):
        self.ports = ports
        self.status = status
        self.points = {}

    def set(self, port, s):
        self.status.setValue(f"setting points {port} to {s}")
        points = self.points.setdefault(port, HardwarePoints(self.ports, port))
        if s == "left":
            points.left()
        if s == "right":
            points.right()
