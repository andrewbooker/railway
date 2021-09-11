
class ReportingListener():
    def __init__(self):
        self.history = []

    def connect(self, section, direction):
        self.history.append((section["id"], direction))

    def setPointsTo(self, s, st, p):
        self.history.append(("%s points selection" % st, s))

    def waitToSetPointsTo(self, s, st, p):
        self.history.append(("%s points condition" % st, s))


def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


from model import *
class NavigateModel():
    def __init__(self, model, listener):
        self.model = model
        self.listener = listener
        self.pointsSelection = lambda: "left"
        self.pointsCourse = None
        for s in model.sections:
            self.occupy = (s, "forward")
            return

    def initialDirection(self, d):
        self.occupy = (self.occupy[0], d)

    @staticmethod
    def opposite(d):
        return "reverse" if d == "forward" else "forward"

    def next(self):
        (sectionId, direction) = self.occupy
        section = self.model.sections[sectionId]

        if (direction == "forward" and section.next is None) or (direction == "reverse" and section.previous is None):
            self.occupy = (sectionId, NavigateModel.opposite(direction))
        elif direction == "forward" and section.next is not None:
            self.occupy = section.next
        elif direction == "reverse" and section.previous is not None:
            self.occupy = section.previous
        self.listener.connect({"id": sectionId}, direction)

        if section.__class__ == Points:
            if self.pointsCourse is None and direction == "forward":
                self.listener.setPointsTo(self.pointsSelection(), "outgoing", section)
                self.pointsCourse = section.outgoing.left
            if self.pointsCourse is not None and direction == "reverse":
                self.listener.waitToSetPointsTo(self.pointsSelection(), "outgoing", section)
                self.pointsCourse = None

def test_shuttle():
    m = Model(openLayout("example-layouts/shuttle.json"))
    listener = ReportingListener()
    nm = NavigateModel(m, listener)

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
    nm = NavigateModel(m, listener)

    nm.next()
    assert listener.history == [("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "forward")]

def test_single_loop_reverse():
    m = Model(openLayout("example-layouts/single-loop.json"))
    listener = ReportingListener()
    nm = NavigateModel(m, listener)
    nm.initialDirection("reverse")

    nm.next()
    assert listener.history == [("s01", "reverse")]
    nm.next()
    assert listener.history == [("s01", "reverse"), ("s01", "reverse")]

def test_two_stage_loop():
    m = Model(openLayout("example-layouts/two-stage-loop.json"))
    listener = ReportingListener()
    nm = NavigateModel(m, listener)

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
    nm = NavigateModel(m, listener)
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
    nm = NavigateModel(m, listener)
    nm.pointsSelection = lambda: "left"

    nm.next()
    assert listener.history == [
        ("p01", "forward"),
        ("outgoing points selection", "left")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("p01", "reverse"),
        ("outgoing points condition", "left")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("p01", "reverse"),
        ("outgoing points condition", "left"),
        ("p01", "forward"),
        ("outgoing points selection", "left")
    ]

def test_self_contained_points_reverse_right():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))
    listener = ReportingListener()
    nm = NavigateModel(m, listener)
    nm.initialDirection("reverse")
    nm.pointsSelection = lambda: "right"

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
        ("p01", "reverse"),
        ("outgoing points condition", "right")
    ]
    nm.next()
    assert listener.history == [
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("p01", "reverse"),
        ("outgoing points condition", "right"),
        ("p01", "forward"),
        ("outgoing points selection", "right")
    ]
