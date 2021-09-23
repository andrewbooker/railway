
class DetectionListener():
    def setNextDetector(self, d, v, description):
        pass

    def waitFor(self, d, state, description):
        pass


class DirectionController():
    def set(self, portId, direction):
        pass


class PointsController():
    def set(self, pId, s):
        pass


from routeIterator import NavigationListener
from model import *


class RouteNavigator(NavigationListener):
    def __init__(self, model: Model, directionController: DirectionController, detectionListener: DetectionListener, pointsController: PointsController):
        self.model = model
        self.detectionListener = detectionListener
        self.directionController = directionController
        self.pointsController = pointsController
        self.currentDirection = "forward"

    @staticmethod
    def portId(p):
        return "%s_%s" % (p[0], p[1])

    def connect(self, sId, direction):
        section = self.model.sections[sId["id"]]
        self.currentDirection = direction
        self.directionController.set(RouteNavigator.portId(section.direction), self.currentDirection)
        if direction == "forward" and section.forwardUntil is not None:
            self.detectionListener.setNextDetector(RouteNavigator.portId(section.forwardUntil), 1, "forwardUntil")
        if direction == "reverse" and section.reverseUntil is not None:
            self.detectionListener.setNextDetector(RouteNavigator.portId(section.reverseUntil), 1, "reverseUntil")

        if direction == "forward" and section.next is not None and section.next.__class__.__name__ != "Stage":
            nextSection = self.model.sections[section.next[0]]
            if nextSection.__class__.__name__ == "Points":
                pointsStage = nextSection.next if nextSection.next.__class__.__name__ == "Stage" else getattr(nextSection, section.next[2])
                self.detectionListener.setNextDetector(RouteNavigator.portId(pointsStage.detector), 0, "from section to points")
            elif section.__class__.__name__ == "Points" and section.outgoing is not None:
                self.detectionListener.setNextDetector(RouteNavigator.portId(section.outgoing.detector), 1, "from points to next section")
            return
        if direction == "reverse" and section.previous is not None and section.previous.__class__.__name__ != "Stage":
            previousSection = self.model.sections[section.previous[0]]
            if previousSection.__class__.__name__ == "Points":
                pointsStage = previousSection.previous if previousSection.previous.__class__.__name__ == "Stage" else getattr(previousSection, section.next[2])
                self.detectionListener.setNextDetector(RouteNavigator.portId(pointsStage.detector), 0, "from section to points")
            elif section.__class__.__name__ == "Points" and section.incoming is not None:
                self.detectionListener.setNextDetector(RouteNavigator.portId(getattr(section, "incoming").detector), 1, "from points to next section")


    def _traversePoints(self, stage, selection):
        self.pointsController.set(RouteNavigator.portId(stage.selector), selection)
        self.detectionListener.setNextDetector(RouteNavigator.portId(stage.detector), 1, "from points to next section")

    def setPointsTo(self, s, st, p):
        points = self.model.sections[p["id"]]
        stage = getattr(points, st)
        setPoints = lambda: self._traversePoints(stage, s)
        self.detectionListener.waitFor(RouteNavigator.portId(stage.detector), 0, "selection (divergence)").then(setPoints)

    def waitToSetPointsTo(self, s, st, p):
        points = self.model.sections[p["id"]]
        stage = getattr(points, st)
        setPoints = lambda: self._traversePoints(stage, s)
        self.detectionListener.waitFor(RouteNavigator.portId(stage.detector), 0, "condition (convergence)").then(setPoints)