from lib.monitor import StatusComponent
from lib.ports import Ports
from lib.routeNavigator import DirectionController


class DirectionRelays(DirectionController):
    def __init__(self, device: Ports, status: StatusComponent):
        DirectionController.__init__(self)
        self.device = device
        self.status = status
        self.ports = {}

    def set(self, portId, direction):
        if portId not in self.ports:
            self.ports[portId] = self.device.output(int(portId.split("_")[1]))
        self.status.setValue(f"setting {portId} relay to {direction}")
        self.ports[portId].set(0 if direction == "forward" else 1)
