from lib.ports import Ports


class HardwarePoints:
    LEFT = 9
    RIGHT = 6

    def __init__(self, device: Ports, number: int):
        self.device = device.servoPwmPort(number, HardwarePoints.RIGHT)
        self.val = None

    def _setTo(self, d):
        if d == self.val:
            return
        self.device.set(d)
        self.val = d

    def left(self):
        self._setTo(HardwarePoints.LEFT)

    def right(self):
        self._setTo(HardwarePoints.RIGHT)
