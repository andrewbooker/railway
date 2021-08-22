
from navigator import Journey
from navigationListener import NavigationListener

def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


class LocalDetectionListener():
    def __init__(self):
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

navigation = NavigationListener(detectionListener, directionController, pointsController)


def test_shuttle():
    journey = Journey(openLayout("example-layouts/shuttle.json"), navigation)
    navigation.setNextRequestor(journey.nextStage)
    journey.start()

    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_23"
    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None

    detectionListener.callback()

    assert directionController.direction == "reverse"
    assert directionController.portId == "RPi_23"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None

    detectionListener.callback()
    assert directionController.direction == "forward"
