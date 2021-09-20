
class DetectionListener():
    def setCallback(self, c):
        pass

    def clearCallback(self):
        pass

    def setNextDetector(self, d, v):
        pass

    def waitFor(self, d, state):
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
        self.nextRequestor = None

    @staticmethod
    def portId(p):
        return "%s_%s" % (p[0], p[1])

    def setNextRequestor(self, r):
        self.nextRequestor = r

    def connect(self, sId, direction):
        section = self.model.sections[sId["id"]]
        self.currentDirection = direction
        self.directionController.set(RouteNavigator.portId(section.direction), self.currentDirection)
        if direction == "forward" and section.forwardUntil is not None:
            self.detectionListener.setCallback(self.nextRequestor)
            self.detectionListener.setNextDetector(RouteNavigator.portId(section.forwardUntil), 1)
        if direction == "reverse" and section.reverseUntil is not None:
            self.detectionListener.setCallback(self.nextRequestor)
            self.detectionListener.setNextDetector(RouteNavigator.portId(section.reverseUntil), 1)

        if direction == "forward" and section.next is not None:
            if section.next.__class__ == Stage:
                return
            else:
                nextSection = self.model.sections[section.next[0]]
                if nextSection.__class__ == Points:
                    pointsStage = nextSection.next
                    self.detectionListener.setNextDetector(RouteNavigator.portId(pointsStage.detector), 0)
                    self.detectionListener.setCallback(self.nextRequestor)

    def setPointsTo(self, s, st, p):
        points = self.model.sections[p["id"]]
        stage = getattr(points, st)
        self.detectionListener.waitFor(RouteNavigator.portId(stage.detector), 0)
        self.pointsController.set(RouteNavigator.portId(stage.selector), s)

    def waitToSetPointsTo(self, s, st, p):
        points = self.model.sections[p["id"]]
        stage = getattr(points, st)
        self.detectionListener.setCallback(self.nextRequestor)
        self.detectionListener.setNextDetector(RouteNavigator.portId(stage.detector), 0)
        self.pointsController.set(RouteNavigator.portId(stage.selector), s)
