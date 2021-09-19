
def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()

from model import *
from routeIterator import *


class DetectionListener():
    def setCallback(self, c):
        pass

    def clearCallback(self):
        pass

    def setNextDetector(self, d, v):
        pass

    def waitFor(self, d, state):
        pass

class LocalDetectionListener(DetectionListener):
    def __init__(self):
        self.clear()

    def clear(self):
        self.callback = None
        self.portId = None
        self.value = None

    def clearCallback(self):
        self.callback = None

    def setCallback(self, c):
        self.callback = c

    def setNextDetector(self, d, v):
        self.portId = d
        self.value = v

    def waitFor(self, d, state):
        self.detector = d
        self.value = state


class DirectionController():
    def set(self, portId, direction):
        pass

class LocalDirectionController(DirectionController):
    def __init__(self):
        self.clear()

    def clear(self):
        self.last3 = []

    def set(self, portId, direction):
        if len(self.last3) == 3:
            self.last3.pop(0)
        self.last3.append((portId, direction))

class PointsController():
    def set(self, pId, s):
        pass

class LocalPointsController(PointsController):
    def __init__(self):
        self.last3 = []

    def set(self, pId, s):
        if len(self.last3) == 3:
            self.last3.pop(0)
        self.last3.append((pId, s))


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

        if section.next is not None:
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


def startFrom(fileName):
    m = Model(openLayout(fileName))
    directionController = LocalDirectionController()
    detectionListener = LocalDetectionListener()
    pointsController = LocalPointsController()
    navigator = RouteNavigator(m, directionController, detectionListener, pointsController)
    iterator = RouteIterator(m, navigator)
    navigator.setNextRequestor(iterator.next)
    iterator.next()
    return (detectionListener, directionController, pointsController)


def test_shuttle():
    (detectionListener, directionController) = startFrom("example-layouts/shuttle.json")[:2]

    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse"), ("RPi_23", "forward")]


def test_return_loop():
    (detectionListener, directionController, pointsController) = startFrom("example-layouts/return-loop.json")

    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward")]
    assert pointsController.last3 == []

    detectionListener.callback()
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "forward")]
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert pointsController.last3 == [("RPi_25", "left")]

