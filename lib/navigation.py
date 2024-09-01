from enum import Enum


class PointsSelection(Enum):
    Left = "left"
    Right = "right"

    @staticmethod
    def valueOf(s):
        return PointsSelection.Left if s == PointsSelection.Left.value else PointsSelection.Right


class JunctionOrientation(Enum):
    Convergence = "condition (convergence)"
    Divergence = "selection (divergence)"


class NavigationListener:
    def connect(self, section, direction):
        pass

    def waitToSetPointsTo(self, selection: PointsSelection, st, p, orientation: JunctionOrientation):
        pass


class PointsSelector:
    def select(self) -> PointsSelection:
        pass
