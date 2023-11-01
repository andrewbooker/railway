from routeIterator import NavigationListener
from motionController import MotionController
from model import *


class DetectionListener:
    def setNextDetector(self, d, v, description):
        pass

    def waitFor(self, d, state, description):
        pass


class DirectionController:
    def __init__(self):
        self.direction = None

    def set(self, portId, direction):
        pass

    def currentDirection(self) -> str | None:
        return self.direction


class PointsController:
    def set(self, pId, s):
        pass


class RouteNavigator(NavigationListener):
    def __init__(
            self, model: Model,
            directionController: DirectionController,
            detectionListener: DetectionListener,
            pointsController: PointsController,
            motionController: MotionController
    ):
        self.model = model
        self.detectionListener = detectionListener
        self.directionController = directionController
        self.pointsController = pointsController
        self.motionController = motionController.withChangeDirectionCallback(self.toggleDirection)

    @staticmethod
    def portId(p):
        return "%s_%s" % (p[0], p[1])

    @staticmethod
    def _nextPointsStage(direction, points, stageSpec):
        expectedStage = stageSpec[2] if len(stageSpec) > 2 else None
        if expectedStage is not None:
            return getattr(points, expectedStage)
        if direction == "forward":
            return points.incoming if points.incoming is not None else points.outgoing
        if direction == "reverse":
            return points.outgoing if points.outgoing is not None else points.incoming

    def toggleDirection(self, sId):
        self.connect(sId, "reverse" if self.directionController.currentDirection() == "forward" else "forward")

    def connect(self, sId, direction):
        section = self.model.sections[sId["id"]]
        self.directionController.set(RouteNavigator.portId(section.direction), direction)
        if direction == "forward" and section.forwardUntil is not None:
            self.detectionListener.waitFor(
                RouteNavigator.portId(section.forwardUntil), 1, "forwardUntil"
            ).then(self.motionController.onCheckpoint)
        if direction == "reverse" and section.reverseUntil is not None:
            self.detectionListener.waitFor(
                RouteNavigator.portId(section.reverseUntil), 1, "reverseUntil"
            ).then(self.motionController.onCheckpoint)

        if direction == "forward" and section.next is not None and section.next.__class__.__name__ != "Stage":
            nextSection = self.model.sections[section.next[0]]
            if nextSection.__class__.__name__ == "Points":
                pointsStage = RouteNavigator._nextPointsStage(direction, nextSection, section.next)
                self.detectionListener.setNextDetector(RouteNavigator.portId(pointsStage.detector), 0, "from section to points")
            elif section.__class__.__name__ == "Points" and section.outgoing is not None: # and section.incoming is None:
                self.detectionListener.setNextDetector(RouteNavigator.portId(section.outgoing.detector), 1, "from points to next section")
            return
        if direction == "reverse" and section.previous is not None and section.previous.__class__.__name__ != "Stage":
            previousSection = self.model.sections[section.previous[0]]
            if previousSection.__class__.__name__ == "Points":
                pointsStage = RouteNavigator._nextPointsStage(direction, previousSection, section.previous)
                self.detectionListener.setNextDetector(RouteNavigator.portId(pointsStage.detector), 0, "from section to points")
            elif section.__class__.__name__ == "Points" and section.incoming is not None:  #and section.outgoing is None:
                self.detectionListener.setNextDetector(RouteNavigator.portId(getattr(section, "incoming").detector), 1, "from points to next section")

    def _traversePoints(self, points, stage, selection):
        self.pointsController.set(RouteNavigator.portId(stage.selector), selection)
        if (stage == points.incoming and points.outgoing is None) or (stage == points.outgoing and points.incoming is None):
            self.detectionListener.setNextDetector(RouteNavigator.portId(stage.detector), 1, "traversing points to next section")
        if stage == points.incoming and self.directionController.currentDirection() == "forward":
            self.detectionListener.setNextDetector(RouteNavigator.portId(stage.detector), 1, "traversing incoming points to next section")
        if stage == points.outgoing and self.directionController.currentDirection() == "reverse":
            self.detectionListener.setNextDetector(RouteNavigator.portId(stage.detector), 1, "traversing outgoing points to next section")

    def setPointsTo(self, s, st, p):
        points = self.model.sections[p["id"]]
        stage = getattr(points, st)
        setPoints = lambda: self._traversePoints(points, stage, s)
        self.detectionListener.waitFor(RouteNavigator.portId(stage.detector), 0, "selection (divergence)").then(setPoints)

    def waitToSetPointsTo(self, s, st, p):
        points = self.model.sections[p["id"]]
        stage = getattr(points, st)
        setPoints = lambda: self._traversePoints(points, stage, s)
        self.detectionListener.waitFor(RouteNavigator.portId(stage.detector), 0, "condition (convergence)").then(setPoints)
