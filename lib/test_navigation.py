
from navigator import Journey
from navigationListener import NavigationListener

def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


class LocalDetectionListener():
    def __init__(self):
        self.callback = None
        self.detector = None
        self.value = None

    def clearCallback(self):
        self.callback = None

    def setCallback(self, c):
        self.callback = c

    def setNextDetector(self, d, v):
        self.detector = d
        self.value = v

class LocalDirectionController():
    def __init__(self):
        self.portId = None
        self.direction = None

    def set(self, portId, direction):
        self.portId = portId
        self.direction = direction

class LocalPointsController():
    def set(self):
        pass


detectionListener = LocalDetectionListener()
directionController = LocalDirectionController()
pointsController = LocalPointsController()

listener = NavigationListener(detectionListener, directionController, pointsController)


def test_shuttle_initial_state():
    journey = Journey(openLayout("example-layouts/shuttle.json"), listener)
    journey.start()

    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_23"
    assert detectionListener.detector == "RPi_14"
    assert detectionListener.value == 1
