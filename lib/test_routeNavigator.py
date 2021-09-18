
def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()

from model import *
from routeIterator import *


class DetectionListener():
    def setCallback(self, c):
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


class RouteNavigator(NavigationListener):
    def __init__(self, model: Model, directionController: DirectionController, detectionListener: DetectionListener):
        self.model = model
        self.detectionListener = detectionListener
        self.directionController = directionController
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


def test_shuttle():
    m = Model(openLayout("example-layouts/shuttle.json"))
    directionController = LocalDirectionController()
    detectionListener = LocalDetectionListener()
    navigator = RouteNavigator(m, directionController, detectionListener)
    iterator = RouteIterator(m, navigator)
    navigator.setNextRequestor(iterator.next)
    iterator.next()

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

