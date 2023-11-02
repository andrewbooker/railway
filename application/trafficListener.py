from lib.detectionRouter import DetectionRouter
from lib.ports import Ports


class TrafficListener:
    def __init__(self, detectionRouter: DetectionRouter):
        self.detectionRouter = detectionRouter
        self.detectorInputs = dict()
        self.detectorPorts = dict()
        self.lastRead = dict()

    def registerInputDevices(self, bankName: str, ports: Ports):
        self.detectorInputs[bankName] = ports

    def registerPorts(self, bank, portNumbers):
        for p in portNumbers:
            self.detectorPorts[f"{bank}_{p}"] = self.detectorInputs[bank].input(p)

    def poll(self):
        for portId, inp in self.detectorPorts.items():
            last_val = self.lastRead.get(portId)
            val = inp.get()
            if val != last_val:
                self.detectionRouter.receiveUpdate(portId, val)
                self.lastRead[portId] = val
