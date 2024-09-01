from lib.navigation import *
from lib.routeNavigator import *
from lib.detectionRouter import *
from lib.directionController import Direction


def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


class LeftPointsSelector(PointsSelector):
    def select(self) -> PointsSelection:
        return PointsSelection.Left


class LocalDirectionController(DirectionController):
    def __init__(self):
        DirectionController.__init__(self)
        self.last3 = []

    def clear(self):
        self.last3 = []

    def set(self, portId, direction: Direction):
        super().set(portId, direction)
        if len(self.last3) == 3:
            self.last3.pop(0)
        self.last3.append((portId, direction))


class LocalPointsController(PointsController):
    def __init__(self):
        self.last3 = []

    def set(self, pId, s: PointsSelection):
        if len(self.last3) == 3:
            self.last3.pop(0)
        self.last3.append((pId, s.value))


class LocalMotionController(MotionController):
    def __init__(self):
        self.changeDirectionCallback = None

    def withChangeDirectionCallback(self, cb):
        self.changeDirectionCallback = cb
        return self


class IgnoreStatus:
    def setValue(self, ignore):
        pass


def startFrom(fileName):
    model = Model(openLayout(fileName))
    directionController = LocalDirectionController()
    detectionListener = DetectionRouter(IgnoreStatus())
    motionController = LocalMotionController()
    pointsController = LocalPointsController()
    navigator = RouteNavigator(model, directionController, detectionListener, pointsController, motionController)
    return navigator, detectionListener, directionController, motionController, pointsController


def test_forwards_on_basic_section():
    navigator, detectionListener, directionController, motionController, pointsController = startFrom("example-layouts/shuttle.json")
    assert directionController.last3 == []
    assert detectionListener.awaiting == {}
    assert pointsController.last3 == []
    assert motionController.changeDirectionCallback == navigator.toggleDirection

    expected_forward_until = ("arduino_52", 1)
    navigator.connect({"id": "s01"}, Direction.Forward)

    assert pointsController.last3 == []
    assert directionController.currentDirection() == Direction.Forward
    assert directionController.currentPortId() == "RPi_23"
    assert directionController.last3 == [("RPi_23", Direction.Forward)]
    assert {k for k in detectionListener.awaiting} == {expected_forward_until}
    assert detectionListener.awaiting[expected_forward_until][0] == "forwardUntil"
    assert detectionListener.awaiting[expected_forward_until][1].m == motionController.onCheckpoint


def test_reverse_on_basic_section():
    navigator, detectionListener, directionController, _, _ = startFrom("example-layouts/shuttle.json")

    expected_reverse_until = ("arduino_53", 1)
    navigator.connect({"id": "s01"}, Direction.Reverse)

    assert directionController.currentDirection() == Direction.Reverse
    assert directionController.currentPortId() == "RPi_23"
    assert directionController.last3 == [("RPi_23", Direction.Reverse)]

    assert {k for k in detectionListener.awaiting.keys()} == {expected_reverse_until}
    assert detectionListener.awaiting[expected_reverse_until][0] == "reverseUntil"


def test_changing_direction_on_basic_section_leaves_both_detectors_active():
    navigator, detectionListener, directionController, _, _ = startFrom("example-layouts/shuttle.json")

    expected_forward_until = ("arduino_52", 1)
    expected_reverse_until = ("arduino_53", 1)
    navigator.connect({"id": "s01"}, Direction.Forward)
    navigator.toggleDirection("RPi_23")

    assert directionController.currentDirection() == Direction.Reverse
    assert directionController.currentPortId() == "RPi_23"
    assert directionController.last3 == [("RPi_23", Direction.Forward), ("RPi_23", Direction.Reverse)]
    assert {expected_forward_until, expected_reverse_until} == {k for k in detectionListener.awaiting}
    assert detectionListener.awaiting[expected_forward_until][0] == "forwardUntil"
    assert detectionListener.awaiting[expected_reverse_until][0] == "reverseUntil"


def test_left_arm_of_a_set_of_points():
    navigator, detectionListener, directionController, motionController, pointsController = startFrom("example-layouts/simple-fork.json")
    assert len(detectionListener.awaiting) == 0

    navigator.connect({"id": "s01"}, Direction.Forward)
    assert directionController.last3 == [("RPi_23", Direction.Forward)]
    assert {a for a in detectionListener.awaiting} == {("RPi_17", 0)}
    assert detectionListener.awaiting[("RPi_17", 0)][0] == "from section to points"

