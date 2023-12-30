from lib.model import *
from lib.routeIterator import RouteIterator, NavigationListener, PointsSelector


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

    def setPointsTo(self, s, st, p):
        self.history.append(("%s points selection" % st, s))
        self.lastPoints = (p["id"])

    def waitToSetPointsTo(self, s, st, p):
        self.history.append(("%s points condition" % st, s))
        self.lastPoints = p["id"]


def test_shuttle():
    m = Model(openLayout("example-layouts/shuttle.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)

    assert listener.history == []
    nm.next()
    assert listener.history == [("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "reverse")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "reverse"), ("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "reverse"), ("s01", "forward"), ("s01", "reverse")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "reverse"), ("s01", "forward"), ("s01", "reverse"), ("s01", "forward")]

def test_single_loop():
    m = Model(openLayout("example-layouts/single-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)

    nm.next()
    assert listener.history == [("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "forward")]

def test_single_loop_reverse():
    m = Model(openLayout("example-layouts/single-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)
    nm.initialDirection("reverse")

    nm.next()
    assert listener.history == [("s01", "reverse")]
    nm.next()
    assert listener.history == [("s01", "reverse"), ("s01", "reverse")]

def test_two_stage_loop():
    m = Model(openLayout("example-layouts/two-stage-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)

    nm.next()
    assert listener.history == [("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s02", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s02", "forward"), ("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s02", "forward"), ("s01", "forward"), ("s02", "forward")]

def test_two_stage_loop_reverse():
    m = Model(openLayout("example-layouts/two-stage-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, None)
    nm.initialDirection("reverse")

    nm.next()
    assert listener.history == [("s01", "reverse")]
    nm.next()
    assert listener.history == [("s01", "reverse"), ("s02", "reverse")]
    nm.next()
    assert listener.history == [("s01", "reverse"), ("s02", "reverse"), ("s01", "reverse")]


def test_self_contained_points_forward_left():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.lastPoints == "p01"
    assert listener.history == [
        ("p01", "forward"),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("outgoing points condition", "left"),
        ("p01", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("outgoing points condition", "left"),
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points selection", "left")
    ]


def test_self_contained_points_reverse_right():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, RightPointsSelector())
    nm.initialDirection("reverse")

    nm.next()
    assert listener.history == [
        ("p01", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points selection", "right")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("outgoing points condition", "right"),
        ("p01", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points selection", "right")
    ]


def test_simple_fork_points_left():
    m = Model(openLayout("example-layouts/simple-fork.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.history == [
        ("s01", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("s02", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("s02", "forward"),
        ("s02", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("s02", "forward"),
        ("s02", "reverse"),
        ("outgoing points condition", "left"),
        ("p01", "reverse")
    ]


def test_simple_fork_incoming_points_left():
    m = Model(openLayout("example-layouts/simple-fork-incoming.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.history == [
        ("s01", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("s01", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("incoming points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("incoming points selection", "left"),
        ("s02", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("incoming points selection", "left"),
        ("s02", "reverse"),
        ("s02", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("s01", "forward"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("incoming points selection", "left"),
        ("s02", "reverse"),
        ("s02", "forward"),
        ("incoming points condition", "left"),
        ("p01", "forward")
    ]


def test_return_loops_back_to_back_points_left():
    m = Model(openLayout("example-layouts/return-loops-back-to-back.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, LeftPointsSelector())

    nm.next()
    assert listener.history == [
        ("r01", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "left"),
        ("r02", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "left"),
        ("r02", "forward"),
        ("incoming points condition", "right"),
        ("p01", "forward"),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "left"),
        ("r02", "forward"),
        ("incoming points condition", "right"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("r01", "forward")
    ]


def test_return_loops_back_to_back_points_right():
    m = Model(openLayout("example-layouts/return-loops-back-to-back.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener, RightPointsSelector())

    nm.next()
    assert listener.history == [
        ("r01", "forward")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "right")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "right"),
        ("r02", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "right"),
        ("r02", "reverse"),
        ("incoming points condition", "left"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "right"),
        ("r02", "reverse"),
        ("incoming points condition", "left"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("r01", "reverse")
    ]
    nm.next()
    assert listener.history == [
        ("r01", "forward"),
        ("outgoing points condition", "right"),
        ("p01", "reverse"),
        ("incoming points selection", "right"),
        ("r02", "reverse"),
        ("incoming points condition", "left"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("r01", "reverse"),
        ("outgoing points condition", "left"),
        ("p01", "reverse"),
        ("incoming points selection", "right")
    ]
