from lib.hardwarePoints import HardwarePoints
from lib.monitor import StatusComponent
from lib.ports import Ports
from lib.routeNavigator import PointsController
from lib.navigation import PointsSelection


class ServoPointsController(PointsController):
    def __init__(self, ports: Ports, status: StatusComponent):
        self.ports = ports
        self.status = status
        self.points = dict()

    def set(self, port, s: PointsSelection):
        self.status.setValue(f"setting points {port} to {s.name}")
        if port not in self.points:
            self.status.setValue(f"registering points at {port}")
            port_number = int(port.split("_")[1])
            self.points[port] = HardwarePoints(self.ports, port_number)

        points = self.points[port]
        if s == PointsSelection.Left:
            points.left()
        if s == PointsSelection.Right:
            points.right()
