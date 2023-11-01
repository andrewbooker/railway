
def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


from routeIterator import *
from routeNavigator import *
from detectionRouter import *


class LeftPointsSelector(PointsSelector):
    def select(self):
        return "left"


class LocalDirectionController(DirectionController):
    def __init__(self):
        DirectionController.__init__(self)
        self.last3 = []

    def clear(self):
        self.last3 = []

    def set(self, portId, direction):
        self.direction = direction
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


class LocalMotionController:
    def __init__(self):
        self.changeDirectionCallback = None

    def withChangeDirectionCallback(self, cb):
        self.changeDirectionCallback = cb
        return self

    def onCheckpoint(self):
        self.changeDirectionCallback({"id": "s01"})


def startFrom(fileName):
    m = Model(openLayout(fileName))

    directionController = LocalDirectionController()
    detectionListener = DetectionRouter()
    pointsController = LocalPointsController()
    navigator = RouteNavigator(m, directionController, detectionListener, pointsController, LocalMotionController())
    iterator = RouteIterator(m, navigator, LeftPointsSelector())
    cb = AndThen()
    cb.then(iterator.next)
    detectionListener.setCallback(cb)
    iterator.next()
    return (detectionListener, directionController, pointsController)


def test_shuttle():
    (detectionListener, directionController) = startFrom("example-layouts/shuttle.json")[:2]

    assert directionController.currentDirection() == "forward"
    assert directionController.last3 == [("RPi_23", "forward")]

    detectionListener.receiveUpdate("arduino_52", 1)
    assert directionController.currentDirection() == "reverse"
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse")]

    detectionListener.receiveUpdate("arduino_53", 1)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse"), ("RPi_23", "forward")]


def test_return_loop():
    (detectionListener, directionController, pointsController) = startFrom("example-layouts/return-loop.json")

    assert directionController.last3 == [("RPi_23", "forward")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "forward")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "selection (divergence)"
    assert len(detectionListener.awaiting) == 1

    detectionListener.receiveUpdate("RPi_15", 0)
    assert pointsController.last3 == [("RPi_25", "left")]
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "forward")]
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing points to next section"

    detectionListener.receiveUpdate("RPi_15", 1)
    assert pointsController.last3 == [("RPi_25", "left")]
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "forward"), ("RPi_24", "forward")]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_26", "forward"), ("RPi_24", "forward"), ("RPi_26", "reverse")]
    assert pointsController.last3 == [("RPi_25", "left")]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "condition (convergence)"
    assert len(detectionListener.awaiting) == 1

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_26", "forward"), ("RPi_24", "forward"), ("RPi_26", "reverse")]
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right")]
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing outgoing points to next section"

    detectionListener.receiveUpdate("RPi_15", 1)
    assert directionController.last3 == [("RPi_24", "forward"), ("RPi_26", "reverse"), ("RPi_23", "reverse")]
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right")]
    assert detectionListener.awaiting[("RPi_14", 1)][0] == "reverseUntil"

    detectionListener.receiveUpdate("RPi_14", 1)
    assert directionController.last3 == [("RPi_26", "reverse"), ("RPi_23", "reverse"), ("RPi_23", "forward")]
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right")]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "reverse"), ("RPi_23", "forward"), ("RPi_23", "forward")]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"
    assert len(detectionListener.awaiting) == 1

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "forward"), ("RPi_26", "forward")]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "selection (divergence)"
    assert len(detectionListener.awaiting) == 1

    detectionListener.receiveUpdate("RPi_15", 0)
    assert pointsController.last3 == [("RPi_25", "left"), ("RPi_25", "right"), ("RPi_25", "left")]
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "forward"), ("RPi_26", "forward")]
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing points to next section"


def test_return_loop_incoming_reverse():
    (detectionListener, directionController, pointsController) = startFrom("example-layouts/return-loop-incoming-reverse.json")

    assert directionController.last3 == [("RPi_23", "forward")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_14", 1)][0] == "forwardUntil"

    detectionListener.receiveUpdate("RPi_14", 1)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_23", "reverse"), ("RPi_23", "reverse")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "reverse"), ("RPi_23", "reverse"), ("RPi_26", "reverse")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "selection (divergence)"
    assert len(detectionListener.awaiting) == 1

    detectionListener.receiveUpdate("RPi_15", 0)
    assert pointsController.last3 == [("RPi_25", "left")]
    assert directionController.last3 == [("RPi_23", "reverse"), ("RPi_23", "reverse"), ("RPi_26", "reverse")]
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing points to next section"

    detectionListener.receiveUpdate("RPi_15", 1)
    assert pointsController.last3 == [("RPi_25", "left")]
    assert directionController.last3 == [("RPi_23", "reverse"), ("RPi_26", "reverse"), ("RPi_24", "forward")]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert pointsController.last3 == [("RPi_25", "left")]
    assert directionController.last3 == [('RPi_26', 'reverse'), ('RPi_24', 'forward'), ('RPi_26', 'forward')]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "condition (convergence)"
    assert len(detectionListener.awaiting) == 1

    detectionListener.receiveUpdate("RPi_15", 0)
    assert pointsController.last3 == [("RPi_25", "left"), ('RPi_25', 'right')]
    assert directionController.last3 == [('RPi_26', 'reverse'), ('RPi_24', 'forward'), ('RPi_26', 'forward')]
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing incoming points to next section"

    detectionListener.receiveUpdate("RPi_15", 1)
    assert pointsController.last3 == [("RPi_25", "left"), ('RPi_25', 'right')]
    assert directionController.last3 == [('RPi_24', 'forward'), ('RPi_26', 'forward'), ("RPi_23", "forward")]
    assert detectionListener.awaiting[("RPi_14", 1)][0] == "forwardUntil"

    detectionListener.receiveUpdate("RPi_14", 1)
    assert directionController.last3 == [('RPi_26', 'forward'), ("RPi_23", "forward"), ("RPi_23", "reverse")]
    assert pointsController.last3 == [('RPi_25', 'left'), ('RPi_25', 'right')]
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"


def test_return_loops_back_to_back():
    (detectionListener, directionController, pointsController) = startFrom("example-layouts/return-loops-back-to-back.json")

    assert directionController.last3 == [("RPi_23", "forward")]
    assert pointsController.last3 == []
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "reverse")]
    assert pointsController.last3 == []
    assert len(detectionListener.awaiting) == 2
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "condition (convergence)"
    assert detectionListener.awaiting[("RPi_16", 0)][0] == "selection (divergence)"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "reverse")]
    assert pointsController.last3 == [("RPi_25", "right")]
    assert len(detectionListener.awaiting) == 2
    assert detectionListener.awaiting[("RPi_16", 0)][0] == "selection (divergence)"
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing outgoing points to next section"

    detectionListener.receiveUpdate("RPi_16", 0)
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "reverse")]
    assert pointsController.last3 == [("RPi_25", "right"), ("RPi_27", "left")]
    assert detectionListener.awaiting[("RPi_15", 1)][0] == "traversing outgoing points to next section"

    # maybe something missing in between here, should not proceed to next section until (RPi_16, 1)
    detectionListener.receiveUpdate("RPi_15", 1)
    assert pointsController.last3 == [("RPi_25", "right"), ("RPi_27", "left")]
    assert directionController.last3 == [("RPi_23", "forward"), ("RPi_26", "reverse"), ("RPi_24", "forward")]
    assert detectionListener.awaiting[("RPi_16", 0)][0] == "from section to points"

    detectionListener.receiveUpdate("RPi_16", 0)
    assert pointsController.last3 == [("RPi_25", "right"), ("RPi_27", "left")]
    assert directionController.last3 == [("RPi_26", "reverse"), ("RPi_24", "forward"), ("RPi_26", "forward")]
    assert len(detectionListener.awaiting) == 2
    assert detectionListener.awaiting[("RPi_16", 0)][0] == "condition (convergence)"
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "selection (divergence)"

    detectionListener.receiveUpdate("RPi_16", 0)
    assert pointsController.last3 == [("RPi_25", "right"), ("RPi_27", "left"), ("RPi_27", "right")]
    assert directionController.last3 == [("RPi_26", "reverse"), ("RPi_24", "forward"), ("RPi_26", "forward")]
    assert len(detectionListener.awaiting) == 2
    assert detectionListener.awaiting[("RPi_15", 0)][0] == "selection (divergence)"
    assert detectionListener.awaiting[("RPi_16", 1)][0] == "traversing incoming points to next section"

    detectionListener.receiveUpdate("RPi_15", 0)
    assert pointsController.last3 == [("RPi_27", "left"), ("RPi_27", "right"), ("RPi_25", "left")]
    assert directionController.last3 == [("RPi_26", "reverse"), ("RPi_24", "forward"), ("RPi_26", "forward")]
    assert detectionListener.awaiting[("RPi_16", 1)][0] == "traversing incoming points to next section"

    detectionListener.receiveUpdate("RPi_16", 1)
    assert directionController.last3 == [("RPi_24", "forward"), ("RPi_26", "forward"), ("RPi_23", "forward")]
    assert pointsController.last3 == [("RPi_27", "left"), ("RPi_27", "right"), ("RPi_25", "left")]
