from model import *

class NavigationListener():
    def connect(self, section, direction):
        pass

    def setPointsTo(self, s, st, p):
        pass

    def waitToSetPointsTo(self, s, st, p):
        pass

class RouteIterator():
    def __init__(self, model, listener: NavigationListener):
        self.model = model
        self.listener = listener
        self.pointsSelection = lambda: "left"
        self.initialDir = "forward"
        self.current = None

    def initialDirection(self, d):
        self.initialDir = d

    @staticmethod
    def opposite(d):
        return "reverse" if d == "forward" else "forward"

    @staticmethod
    def possibleNextSection(direction, section, sectionId, isPoints):
        if direction == "forward" and section.next is not None:
            return section.next
        if direction == "reverse" and section.previous is not None:
            return section.previous
        if not isPoints and ((direction == "forward" and section.next is None) or (direction == "reverse" and section.previous is None)):
            return (sectionId, RouteIterator.opposite(direction))
        if (direction == "forward" and section.forwardUntil is not None) or (direction == "reverse" and section.reverseUntil is not None):
            return (sectionId, RouteIterator.opposite(direction))
        return None

    @staticmethod
    def currentStage(approachingConvergence, current, nextSection, section):
        if approachingConvergence:
            return current[2]
        elif nextSection.__class__.__name__ == "Stage":
            return "outgoing" if nextSection == section.outgoing else "incoming"
        return None

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
            self.listener.waitToSetPointsTo(current[3], currentStage, {"id": sectionId})
            self.listener.connect({"id": sectionId}, direction)
            if nextSection.__class__.__name__ == "Stage":
                nextStage = "incoming" if nextSection == section.incoming else "outgoing"
                self._approachDivergence(nextStage, direction, nextSection, section, sectionId)
        else:
            stage = getattr(section, currentStage)
            self.listener.connect({"id": sectionId}, direction)
            self._approachDivergence(currentStage, direction, stage, section, sectionId)

    def _approachDivergence(self, stage, direction, nextSection, section, sectionId):
        selection = self.pointsSelection()
        self.listener.setPointsTo(selection, stage, {"id": sectionId})
        course = getattr(nextSection, selection)
        if stage == "outgoing":
            if course.next is not None:
                self._proceedTo(course.next)
            elif course.forwardUntil is not None:
                self._proceedTo((sectionId, RouteIterator.opposite(direction), stage, selection))
        else:
            if course.previous is not None:
                self._proceedTo(course.previous)
            elif course.reverseUntil is not None:
                self._proceedTo((sectionId, RouteIterator.opposite(direction), stage, selection))

    def _proceedTo(self, to):
        self.current = to
