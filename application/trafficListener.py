from lib.detectionRouter import DetectionRouter
from lib.ports import Ports


class TrafficListener:
    def __init__(self, detectionRouter: DetectionRouter):
        self.detectionRouter = detectionRouter
        self.detectorInputs = dict()
        self.detectorPorts = dict()

    def registerInputDevices(self, bankName: str, ports: Ports):
        self.detectorInputs[bankName] = ports

    def registerPorts(self, bank, portNumbers):
        for p in portNumbers:
            self.detectorPorts[f"{bank}_{p}"] = self.detectorInputs[bank].input(p)

    def poll(self):
        for portId, inp in self.detectorPorts.items():
            self.detectionRouter.receiveUpdate(portId, inp.get())
