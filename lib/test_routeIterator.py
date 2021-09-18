
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
class RouteIterator():
    def __init__(self, model, listener):
        self.model = model
        self.listener = listener
        self.pointsSelection = lambda: "left"
        self.initialDir = "forward"
        self.current = None

    def initialDirection(self, d):
        self.initialDir = d

    @staticmethod
    def opposite(d):
        return "reverse" if d == "forward" else "forward"

    @staticmethod
    def possibleNextSection(direction, section, sectionId, isPoints):
        if direction == "forward" and section.next is not None:
            return section.next
        if direction == "reverse" and section.previous is not None:
            return section.previous
        if not isPoints and ((direction == "forward" and section.next is None) or (direction == "reverse" and section.previous is None)):
            return (sectionId, RouteIterator.opposite(direction))
        if (direction == "forward" and section.forwardUntil is not None) or (direction == "reverse" and section.reverseUntil is not None):
            return (sectionId, RouteIterator.opposite(direction))
        return None

    @staticmethod
    def currentStage(approachingConvergence, current, nextSection, section):
        if approachingConvergence:
            return current[2]
        elif nextSection.__class__ == Stage:
            return "outgoing" if nextSection == section.outgoing else "incoming"
        return None

    def next(self):
        if self.current is None:
            for s in self.model.sections:
                self._proceedTo((s, self.initialDir))
                break
        current = self.current
        (sectionId, direction) = current[:2]
        section = self.model.sections[sectionId]
        isPoints = section.__class__ == Points
        nextSection = RouteIterator.possibleNextSection(direction, section, sectionId, isPoints)
        if nextSection is not None and nextSection.__class__ != Stage:
            self._proceedTo(nextSection)

        approachingConvergence = len(current) > 2
        currentStage = RouteIterator.currentStage(approachingConvergence, current, nextSection, section)

        if not isPoints or currentStage is None:
            self.listener.connect({"id": sectionId}, direction)
            return

        if approachingConvergence:
            self.listener.waitToSetPointsTo(current[3], currentStage, section)
            self.listener.connect({"id": sectionId}, direction)
            if nextSection.__class__ == Stage:
                nextStage = "incoming" if nextSection == section.incoming else "outgoing"
                self._approachDivergence(nextStage, direction, nextSection, section, sectionId)
        else:
            stage = getattr(section, currentStage)
            self.listener.connect({"id": sectionId}, direction)
            self._approachDivergence(currentStage, direction, stage, section, sectionId)

    def _approachDivergence(self, stage, direction, nextSection, section, sectionId):
        selection = self.pointsSelection()
        self.listener.setPointsTo(selection, stage, section)
        course = getattr(nextSection, selection)
        if stage == "outgoing":
            if course.next is not None:
                self._proceedTo(course.next)
            elif course.forwardUntil is not None:
                self._proceedTo((sectionId, RouteIterator.opposite(direction), stage, selection))
        else:
            if course.previous is not None:
                self._proceedTo(course.previous)
            elif course.reverseUntil is not None:
                self._proceedTo((sectionId, RouteIterator.opposite(direction), stage, selection))

    def _proceedTo(self, to):
        self.current = to


def test_shuttle():
    m = Model(openLayout("example-layouts/shuttle.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener)

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
    nm = RouteIterator(m, listener)

    nm.next()
    assert listener.history == [("s01", "forward")]
    nm.next()
    assert listener.history == [("s01", "forward"), ("s01", "forward")]

def test_single_loop_reverse():
    m = Model(openLayout("example-layouts/single-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener)
    nm.initialDirection("reverse")

    nm.next()
    assert listener.history == [("s01", "reverse")]
    nm.next()
    assert listener.history == [("s01", "reverse"), ("s01", "reverse")]

def test_two_stage_loop():
    m = Model(openLayout("example-layouts/two-stage-loop.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener)

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
    nm = RouteIterator(m, listener)
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
    nm = RouteIterator(m, listener)
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
    nm = RouteIterator(m, listener)
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
    nm = RouteIterator(m, listener)
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


def test_simple_fork_incoming_points_left():
    m = Model(openLayout("example-layouts/simple-fork-incoming.json"))
    listener = ReportingListener()
    nm = RouteIterator(m, listener)
    nm.pointsSelection = lambda: "left"

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
    nm = RouteIterator(m, listener)
    nm.pointsSelection = lambda: "left"

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
    nm = RouteIterator(m, listener)
    nm.pointsSelection = lambda: "right"

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
