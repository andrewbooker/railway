from enum import Enum


class Direction(Enum):
    Forward = "forward"
    Reverse = "reverse"


class DirectionController:
    def __init__(self):
        self.direction: Direction | None = None
        self.portId = None

    def set(self, portId, direction: Direction):
        self.direction = direction
        self.portId = portId

    def currentDirection(self):
        return self.direction

    def currentPortId(self):
        return self.portId
