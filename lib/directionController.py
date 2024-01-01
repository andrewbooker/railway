from enum import Enum


class Direction(Enum):
    Forward = "forward"
    Reverse = "reverse"

    @staticmethod
    def value_of(s: str):
        for d in Direction:
            if d.value == s:
                return d
        return Direction.Forward

    def opposite(self):
        return Direction.Reverse if self == Direction.Forward else Direction.Forward


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
