
def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()

from model import *
from routeIterator import *
from routeNavigator import *


class LocalDetectionListener(DetectionListener):
    def __init__(self):
        self.clear()

    def clear(self):
        self.callback = None
        self.portId = None
        self.value = None

    def clearCallback(self):
        self.clear()

    def setCallback(self, c):
        self.callback = c

    def setNextDetector(self, d, v):
        self.portId = d
        self.value = v

    def waitFor(self, d, state):
        self.detector = d
        self.value = state


class LocalDirectionController(DirectionController):
    def __init__(self):
        self.clear()

    def clear(self):
        self.last3 = []

    def set(self, portId, direction):
        if len(self.last3) == 3:
            self.last3.pop(0)
        self.last3.append((portId, direction))


class LocalPointsController(PointsController):
    def __init__(self):
        self.last3 = []

    def set(self, pId, s):
        if len(self.last3) == 3:
            self.last3.pop(0)
        self.last3.append((pId, s))


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

    assert detectionListener.portId == "arduino_52"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward")]

    detectionListener.callback()
    assert detectionListener.portId == "arduino_53"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse")]

    detectionListener.callback()
    assert detectionListener.portId == "arduino_52"
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

    detectionListener.callback()
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "forward"), ("RPi_24", "forward")]
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert pointsController.last3 == [("RPi_25", "left")]

    detectionListener.callback()
    assert directionController.last3 == [("RPi_26", "forward"), ("RPi_24", "forward"), ("RPi_26", "reverse")]
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right")]

    detectionListener.callback()
    assert directionController.last3 == [("RPi_24", "forward"), ("RPi_26", "reverse"), ("RPi_23", "reverse")]
    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_26", "reverse"), ("RPi_23", "reverse"), ("RPi_23", "forward")]
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "reverse"), ("RPi_23", "forward"), ("RPi_26", "forward")]
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right"), ("RPi_25", "left")]


def test_return_loops_back_to_back():
    (detectionListener, directionController, pointsController) = startFrom("example-layouts/return-loops-back-to-back.json")

    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward")]
    assert pointsController.last3 == []

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"  # should be a list of 15 and 16
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "reverse")]
    assert pointsController.last3 == [("RPi_25", "right"), ("RPi_27", "left")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"  # should be a list of 15 and 16
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "reverse"), ("RPi_24", "forward")]
    assert pointsController.last3 == [("RPi_25", "right"), ("RPi_27", "left")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_26", "reverse"), ("RPi_24", "forward"), ("RPi_26", "forward")]
    assert pointsController.last3 == [("RPi_27", "left"), ("RPi_27", "right"), ("RPi_25", "left")]

    detectionListener.callback()
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert directionController.last3 == [("RPi_24", "forward"), ("RPi_26", "forward"), ("RPi_23", "forward")]
    assert pointsController.last3 == [("RPi_27", "left"), ("RPi_27", "right"), ("RPi_25", "left")]
