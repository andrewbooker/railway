
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

    def waitFor(self, d, state):
        self.detector = d
        self.value = state

class LocalDirectionController():
    def __init__(self):
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

    def set(self, pId, s):
        pass

class LocalPointsController(PointsController):
    def __init__(self):
        super().__init__()
        self.port = None
        self.bank = None
        self.selection = None

    def set(self, pId, s):
        self.port = self.points[pId]["selector"]["port"]
        self.bank = self.points[pId]["selector"]["bank"]
        self.selection = s


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

