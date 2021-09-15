
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
        self.initialDir = "forward"
        self.occupy = []


    def initialDirection(self, d):
        self.initialDir = d

    @staticmethod
    def opposite(d):
        return "reverse" if d == "forward" else "forward"

    def next(self):
        if len(self.occupy) == 0:
            for s in self.model.sections:
                self.occupy.append((s, self.initialDir))
                break
        current = self.occupy[-1]
        (sectionId, direction) = current[:2]
        approachingConvergence = len(current) > 2
        currentStage = current[2] if approachingConvergence else "outgoing"
        currentSelection = current[3] if approachingConvergence else None
        section = self.model.sections[sectionId]
        isPoints = section.__class__ == Points

        nextSection = None

        if direction == "forward" and section.next is not None:
            nextSection = section.next
        if direction == "reverse" and section.previous is not None:
            nextSection = section.previous
        if not isPoints and ((direction == "forward" and section.next is None) or (direction == "reverse" and section.previous is None)):
            nextSection = (sectionId, NavigateModel.opposite(direction))
        if (direction == "forward" and section.forwardUntil is not None) or (direction == "reverse" and section.reverseUntil is not None):
            nextSection = (sectionId, NavigateModel.opposite(direction))

        if nextSection is not None:
            self.occupy.append(nextSection)

        if not isPoints or (not approachingConvergence and (currentStage == "outgoing" and direction == "reverse") or (currentStage == "incoming" and direction == "forward")):
            self.listener.connect({"id": sectionId}, direction)
            return

        if approachingConvergence:
            self.listener.waitToSetPointsTo(currentSelection, currentStage, section)
            self.listener.connect({"id": sectionId}, direction)
        else:
            selection = self.pointsSelection()
            stage = getattr(section, currentStage)
            course = getattr(stage, selection)
            self.listener.connect({"id": sectionId}, direction)
            self.listener.setPointsTo(selection, currentStage, section)
            if direction == "forward":
                if course.next is not None:
                    self.occupy.append(course.next)
                elif course.forwardUntil is not None:
                    self.occupy.append((sectionId, NavigateModel.opposite(direction), currentStage, selection))
            if direction == "reverse":
                if course.previous is not None:
                    self.occupy.append(course.previous)
                elif course.reverseUntil is not None:
                    self.occupy.append((sectionId, NavigateModel.opposite(direction), currentStage, selection))

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
    nm = NavigateModel(m, listener)
    nm.pointsSelection = lambda: "left"

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
