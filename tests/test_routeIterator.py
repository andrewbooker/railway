from lib.model import *
from lib.routeIterator import *
from lib.directionController import Direction


def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


class LeftPointsSelector(PointsSelector):
    def select(self):
        return "left"


class RightPointsSelector(PointsSelector):
    def select(self):
        return "right"


class ReportingListener(NavigationListener):
    def __init__(self):
        self.history = []
        self.lastPoints = []

    def connect(self, section, direction):
        self.history.append((section["id"], direction))

    def waitToSetPointsTo(self, s: PointsSelection, st, p, orientation: JunctionOrientation):
        action = orientation.value.split(" ")[0]
        self.history.append((f"{st} points {action}", s))
        self.lastPoints = p["id"]


def test_shuttle():
    m = Model(openLayout("example-layouts/shuttle.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)

    assert listener.history == []
    nm.next()
    assert listener.history == [("s01", Direction.Forward)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s01", Direction.Reverse)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s01", Direction.Reverse), ("s01", Direction.Forward)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s01", Direction.Reverse), ("s01", Direction.Forward), ("s01", Direction.Reverse)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s01", Direction.Reverse), ("s01", Direction.Forward), ("s01", Direction.Reverse), ("s01", Direction.Forward)]


def test_single_loop():
    m = Model(openLayout("example-layouts/single-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)

    nm.next()
    assert listener.history == [("s01", Direction.Forward)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s01", Direction.Forward)]


def test_single_loop_reverse():
    m = Model(openLayout("example-layouts/single-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)
    nm.initialDirection(Direction.Reverse)

    nm.next()
    assert listener.history == [("s01", Direction.Reverse)]
    nm.next()
    assert listener.history == [("s01", Direction.Reverse), ("s01", Direction.Reverse)]


def test_two_stage_loop():
    m = Model(openLayout("example-layouts/two-stage-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)

    nm.next()
    assert listener.history == [("s01", Direction.Forward)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s02", Direction.Forward)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s02", Direction.Forward), ("s01", Direction.Forward)]
    nm.next()
    assert listener.history == [("s01", Direction.Forward), ("s02", Direction.Forward), ("s01", Direction.Forward), ("s02", Direction.Forward)]


def test_two_stage_loop_reverse():
    m = Model(openLayout("example-layouts/two-stage-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)
    nm.initialDirection(Direction.Reverse)

    nm.next()
    assert listener.history == [("s01", Direction.Reverse)]
    nm.next()
    assert listener.history == [("s01", Direction.Reverse), ("s02", Direction.Reverse)]
    nm.next()
    assert listener.history == [("s01", Direction.Reverse), ("s02", Direction.Reverse), ("s01", Direction.Reverse)]


def test_self_contained_points_forward_left():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.lastPoints == "p01"
    assert listener.history == [
        ("p01", Direction.Forward),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("p01", Direction.Forward),
        ("outgoing points selection", "left"),
        ("outgoing points condition", "left"),
        ("p01", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("p01", Direction.Forward),
        ("outgoing points selection", "left"),
        ("outgoing points condition", "left"),
        ("p01", Direction.Reverse),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left")
    ]


def test_self_contained_points_reverse_right():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, RightPointsSelector())
    nm.initialDirection(Direction.Reverse)

    nm.next()
    assert listener.history == [
        ("p01", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("p01", Direction.Reverse),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right")
    ]
    nm.next()
    assert listener.history == [
        ("p01", Direction.Reverse),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right"),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("p01", Direction.Reverse),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right"),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right")
    ]


def test_simple_fork_points_left():
    m = Model(openLayout("example-layouts/simple-fork.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left"),
        ("s02", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left"),
        ("s02", Direction.Forward),
        ("s02", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left"),
        ("s02", Direction.Forward),
        ("s02", Direction.Reverse),
        ("outgoing points condition", "left"),
        ("p01", Direction.Reverse)
    ]


def test_simple_fork_incoming_points_left():
    m = Model(openLayout("example-layouts/simple-fork-incoming.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("s01", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("s01", Direction.Reverse),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("s01", Direction.Reverse),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left"),
        ("s02", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("s01", Direction.Reverse),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left"),
        ("s02", Direction.Reverse),
        ("s02", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("s01", Direction.Forward),
        ("s01", Direction.Reverse),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left"),
        ("s02", Direction.Reverse),
        ("s02", Direction.Forward),
        ("incoming points condition", "left"),
        ("p01", Direction.Forward)
    ]


def test_return_loops_back_to_back_points_left():
    m = Model(openLayout("example-layouts/return-loops-back-to-back.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left"),
        ("r02", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left"),
        ("r02", Direction.Forward),
        ("incoming points condition", "right"),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "left"),
        ("r02", Direction.Forward),
        ("incoming points condition", "right"),
        ("p01", Direction.Forward),
        ("outgoing points selection", "left"),
        ("r01", Direction.Forward)
    ]


def test_return_loops_back_to_back_points_right():
    m = Model(openLayout("example-layouts/return-loops-back-to-back.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, RightPointsSelector())

    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward)
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "right")
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "right"),
        ("r02", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "right"),
        ("r02", Direction.Reverse),
        ("incoming points condition", "left"),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right"),
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "right"),
        ("r02", Direction.Reverse),
        ("incoming points condition", "left"),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right"),
        ("r01", Direction.Reverse)
    ]
    nm.next()
    assert listener.history == [
        ("r01", Direction.Forward),
        ("outgoing points condition", "right"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "right"),
        ("r02", Direction.Reverse),
        ("incoming points condition", "left"),
        ("p01", Direction.Forward),
        ("outgoing points selection", "right"),
        ("r01", Direction.Reverse),
        ("outgoing points condition", "left"),
        ("p01", Direction.Reverse),
        ("incoming points selection", "right")
    ]
