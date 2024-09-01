from lib.directionController import Direction
from lib.model import Model
from lib.navigation import *


class RouteIterator:
    def __init__(self, model: Model, listener: NavigationListener, pointsSelector: PointsSelector):
        self.model: Model = model
        self.listener: NavigationListener = listener
        self.pointsSelector: PointsSelector = pointsSelector
        self.initialDir: Direction = Direction.Forward
        self.current = None

    def initialDirection(self, d: Direction):
        self.initialDir = d

    @staticmethod
    def possibleNextSection(direction, section, sectionId, isPoints):
        if direction == Direction.Forward and section.next is not None:
            return section.next
        if direction == Direction.Reverse and section.previous is not None:
            return section.previous
        if not isPoints and ((direction == Direction.Forward and section.next is None) or (direction == Direction.Reverse and section.previous is None)):
            return sectionId, direction.opposite()
        if (direction == Direction.Forward and section.forwardUntil is not None) or (direction == Direction.Reverse and section.reverseUntil is not None):
            return sectionId, direction.opposite()
        return None

    @staticmethod
    def currentStage(approachingConvergence, current, nextSection, section):
        if approachingConvergence:
            return current[2]
        elif nextSection.__class__.__name__ == "Stage":
            return "outgoing" if nextSection == section.outgoing else "incoming"
        return None

    def startAtSection(self, sectionId):
        self._proceedTo((sectionId, self.initialDir))

    def next(self):
        if self.current is None:
            for s in self.model.sections:
                self._proceedTo((s, self.initialDir))
                break
        current = self.current
        (sectionId, direction) = current[:2]
        section = self.model.sections[sectionId]
        isPoints = section.__class__.__name__ == "Points"
        nextSection = RouteIterator.possibleNextSection(direction, section, sectionId, isPoints)
        if nextSection is not None and nextSection.__class__.__name__ != "Stage":
            self._proceedTo(nextSection)

        approachingConvergence = len(current) > 2
        currentStage = RouteIterator.currentStage(approachingConvergence, current, nextSection, section)

        if not isPoints or currentStage is None:
            self.listener.connect({"id": sectionId}, direction)
            return

        if approachingConvergence:
            self.listener.waitToSetPointsTo(current[3], currentStage, {"id": sectionId}, JunctionOrientation.Convergence)
            self.listener.connect({"id": sectionId}, direction)
            if nextSection.__class__.__name__ == "Stage":
                nextStage = "incoming" if nextSection == section.incoming else "outgoing"
                self._approachDivergence(nextStage, direction, nextSection, sectionId)
        else:
            stage = getattr(section, currentStage)
            self.listener.connect({"id": sectionId}, direction)
            self._approachDivergence(currentStage, direction, stage, sectionId)

    def _approachDivergence(self, stage, direction, nextSection, sectionId):
        selection = self.pointsSelector.select()
        self.listener.waitToSetPointsTo(selection, stage, {"id": sectionId}, JunctionOrientation.Divergence)
        course = getattr(nextSection, selection.value)
        if stage == "outgoing":
            if course.next is not None:
                self._proceedTo(course.next)
            elif course.forwardUntil is not None:
                self._proceedTo((sectionId, direction.opposite(), stage, selection))
        else:
            if course.previous is not None:
                self._proceedTo(course.previous)
            elif course.reverseUntil is not None:
                self._proceedTo((sectionId, direction.opposite(), stage, selection))

    def _proceedTo(self, to):
        self.current = to
