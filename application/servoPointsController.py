from lib.hardwarePoints import HardwarePoints
from lib.monitor import StatusComponent
from lib.ports import Ports
from lib.routeNavigator import PointsController


class ServoPointsController(PointsController):
    def __init__(self, ports: Ports, status: StatusComponent):
        self.ports = ports
        self.status = status
        self.points = dict()

    def set(self, port, s):
        self.status.setValue(f"setting points {port} to {s}")
        if port not in self.points:
            self.status.setValue(f"registering points at {port}")
            port_number = int(port.split("_")[1])
            self.points[port] = HardwarePoints(self.ports, port_number)

        points = self.points[port]
        if s == "left":
            points.left()
        if s == "right":
            points.right()
