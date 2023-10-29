
class HardwarePoints():
    LEFT = 9
    RIGHT = 6

    def __init__(self, device):
        self.device = device
        self.val = HardwarePoints.RIGHT

    def _setTo(self, d, desc):
        if d == self.val:
            return
        self.device.set(d)
        self.val = d
        print("set to", desc)

    def left(self):
        self._setTo(HardwarePoints.LEFT, "left")

    def right(self):
        self._setTo(HardwarePoints.RIGHT, "right")

