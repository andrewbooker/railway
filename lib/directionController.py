class DirectionController:
    def __init__(self):
        self.direction = None
        self.portId = None

    def set(self, portId, direction):
        self.direction = direction
        self.portId = portId

    def currentDirection(self):
        return self.direction

    def currentPortId(self):
        return self.portId
