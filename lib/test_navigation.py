
from navigator import Journey
from navigationListener import NavigationListener
import pytest

def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


class LocalDetectionListener():
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

class LocalDirectionController():
    def __init__(self):
        self.clear()

    def clear(self):
        self.portId = None
        self.direction = None

    def set(self, portId, direction):
        self.portId = portId
        self.direction = direction

# copied from run.py and semi-real. Should be moved into lib.points once that has been decoupled from RPi
class PointsController():
    def __init__(self):
        self.points = {}

    def fromLayout(self, layout):
        for p in layout:
            if "type" in p and p["type"] == "points":
                self.points[p["id"]] = p

    def fromId(self, pId):
        return self.points[pId]

    def set(self, pId, stage, s):
        pass

class LocalPointsController(PointsController):
    def __init__(self):
        super().__init__()
        self.clear()

    def clear(self):
        self.points = {}
        self.port = None
        self.bank = None
        self.selection = None

    def set(self, pId, stage, s):
        self.port = self.points[pId][stage]["selector"]["port"]
        self.bank = self.points[pId][stage]["selector"]["bank"]
        self.selection = s


detectionListener = LocalDetectionListener()
directionController = LocalDirectionController()
pointsController = LocalPointsController()

navigation = NavigationListener(detectionListener, directionController, pointsController)

@pytest.fixture(autouse=True)
def run_around_tests():
    detectionListener.clear()
    directionController.clear()
    pointsController.clear()
    yield

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

def test_return_loop_points_left():
    layout = openLayout("example-layouts/return-loop.json")
    journey = Journey(layout, navigation)
    pointsController.fromLayout(journey.layout)
    journey.selectPoints = lambda: "left"
    navigation.setNextRequestor(journey.nextStage)
    journey.start()

    assert pointsController.port == None
    assert pointsController.bank == None
    assert pointsController.selection == None

    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_23"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0 # waiting for points to be clear
    assert detectionListener.callback is not None
    assert navigation.currentSection["name"] == "main branch"

    detectionListener.callback() # straight from points onto return loop in forwards direction
    assert pointsController.port == 25
    assert pointsController.bank == "RPi"
    assert pointsController.selection == "left"
    assert navigation.currentSection["name"] == "return loop"
    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_24"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0 # again waiting for points to be clear
    assert detectionListener.callback is not None

    detectionListener.callback()
    assert pointsController.selection == "right"
    assert navigation.currentSection["name"] == "main branch"
    assert directionController.portId == "RPi_23"
    assert directionController.direction == "reverse"
    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1 # waiting to hit the end of main branch

    detectionListener.callback()
    assert directionController.direction == "forward"

def test_return_loop_points_right():
    layout = openLayout("example-layouts/return-loop.json")
    journey = Journey(layout, navigation)
    pointsController.fromLayout(journey.layout)
    journey.selectPoints = lambda: "right"
    navigation.setNextRequestor(journey.nextStage)
    journey.start()

    assert pointsController.port == None
    assert pointsController.bank == None
    assert pointsController.selection == None

    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_23"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert navigation.currentSection["name"] == "main branch"

    detectionListener.callback()
    assert pointsController.port == 25
    assert pointsController.bank == "RPi"
    assert pointsController.selection == "right"
    assert navigation.currentSection["name"] == "return loop"
    assert directionController.direction == "reverse"
    assert directionController.portId == "RPi_24"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None

    detectionListener.callback()
    assert pointsController.selection == "left"
    assert navigation.currentSection["name"] == "main branch"
    assert directionController.portId == "RPi_23"
    assert directionController.direction == "reverse"
    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1

    detectionListener.callback()
    assert directionController.direction == "forward"

def test_single_loop():
    layout = openLayout("example-layouts/single-loop.json")
    journey = Journey(layout, navigation)
    journey.start()

    assert navigation.currentSection["name"] == "main loop"
    assert directionController.portId == "RPi_29"
    assert directionController.direction == "forward"
    assert detectionListener.callback == None
    assert pointsController.port == None
    assert pointsController.bank == None
    assert pointsController.selection == None

def test_single_loop_with_siding_points_right():
    layout = openLayout("example-layouts/single-loop-with-siding.json")
    journey = Journey(layout, navigation)
    pointsController.fromLayout(journey.layout)
    journey.selectPoints = lambda: "right"
    navigation.setNextRequestor(journey.nextStage)
    journey.start()

    assert navigation.currentSection["name"] == "main loop"
    assert directionController.portId == "RPi_23"
    assert directionController.direction == "forward"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None

    for _ in range(3): # go round the loop in reverse indefinitely
        detectionListener.callback()
        assert pointsController.port == 25
        assert pointsController.bank == "RPi"
        assert pointsController.selection == "right"
        assert navigation.currentSection["name"] == "main loop"
        assert directionController.direction == "forward"
        assert directionController.portId == "RPi_23"
        assert detectionListener.portId == "RPi_15"
        assert detectionListener.value == 0
        assert detectionListener.callback is not None


def test_single_loop_with_siding_points_left():
    layout = openLayout("example-layouts/single-loop-with-siding.json")
    journey = Journey(layout, navigation)
    pointsController.fromLayout(journey.layout)
    journey.selectPoints = lambda: "left"
    navigation.setNextRequestor(journey.nextStage)
    journey.start()

    assert navigation.currentSection["name"] == "main loop"
    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_23"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None

    detectionListener.callback()
    assert pointsController.port == 25
    assert pointsController.bank == "RPi"
    assert pointsController.selection == "left"
    assert navigation.currentSection["name"] == "branch siding"
    assert directionController.direction == "forward"
    assert directionController.portId == "RPi_24"
    assert detectionListener.portId == "RPi_14"
    assert detectionListener.value == 1
    assert detectionListener.callback is not None

    detectionListener.callback()
    assert navigation.currentSection["name"] == "branch siding"
    assert directionController.direction == "reverse"
    assert directionController.portId == "RPi_24"
    assert detectionListener.portId == "RPi_15"
    assert detectionListener.value == 0
    assert detectionListener.callback is not None
    assert pointsController.selection == "left"

    for i in range(3): # go round the loop in reverse indefinitely
        detectionListener.callback()
        assert pointsController.selection == "left" if i == 0 else "right"
        assert navigation.currentSection["name"] == "main loop"
        assert directionController.direction == "reverse"
        assert directionController.portId == "RPi_23"
        assert detectionListener.portId == "RPi_15"
        assert detectionListener.value == 0
        assert detectionListener.callback is not None
