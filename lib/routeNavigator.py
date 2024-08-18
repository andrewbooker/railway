
from lib.detectionRouter import DetectionListener
from lib.directionController import DirectionController, Direction
from lib.routeIterator import NavigationListener
from lib.model import *


class PointsController:
    def set(self, pId, s):
        pass


class MotionController:
    def withChangeDirectionCallback(self, cb):
        return self

    def onCheckpoint(self):
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
    def _nextPointsStage(direction: Direction, points, stageSpec):
        expectedStage = stageSpec[2] if len(stageSpec) > 2 else None
        if expectedStage is not None:
            return getattr(points, expectedStage)
        if direction == Direction.Forward:
            return points.incoming if points.incoming is not None else points.outgoing
        if direction == Direction.Reverse:
            return points.outgoing if points.outgoing is not None else points.incoming

    def toggleDirection(self, portId):
        sId = {"id": self.model.sectionFrom(portId)["sId"]}
        self.connect(sId, self.directionController.currentDirection().opposite())

    def connect(self, sId, direction):
        section = self.model.sections[sId["id"]]
        self.directionController.set(RouteNavigator.portId(section.direction), direction)
        if direction == Direction.Forward and section.forwardUntil is not None:
            self.detectionListener.waitFor(
                RouteNavigator.portId(section.forwardUntil), 1, "forwardUntil"
            ).then(self.motionController.onCheckpoint)
        if direction == Direction.Reverse and section.reverseUntil is not None:
            self.detectionListener.waitFor(
                RouteNavigator.portId(section.reverseUntil), 1, "reverseUntil"
            ).then(self.motionController.onCheckpoint)

        if direction == Direction.Forward and section.next is not None and section.next.__class__.__name__ != "Stage":
            nextSection = self.model.sections[section.next[0]]
            if nextSection.__class__.__name__ == "Points":
                pointsStage = RouteNavigator._nextPointsStage(direction, nextSection, section.next)
                self.detectionListener.setNextDetector(RouteNavigator.portId(pointsStage.detector), 0, "from section to points")
            elif section.__class__.__name__ == "Points" and section.outgoing is not None: # and section.incoming is None:
                self.detectionListener.setNextDetector(RouteNavigator.portId(section.outgoing.detector), 1, "from points to next section")
            return
        if direction == Direction.Reverse and section.previous is not None and section.previous.__class__.__name__ != "Stage":
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
        if stage == points.incoming and self.directionController.currentDirection() == Direction.Forward:
            self.detectionListener.setNextDetector(RouteNavigator.portId(stage.detector), 1, "traversing incoming points to next section")
        if stage == points.outgoing and self.directionController.currentDirection() == Direction.Reverse:
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
