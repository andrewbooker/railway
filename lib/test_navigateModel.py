
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
        self.occupy = []
        for s in model.sections:
            self.occupy.append((s, "forward"))
            return

    @staticmethod
    def oppositeDirectionFrom(d):
        return "reverse" if d == "forward" else "forward"

    def next(self):
        if len(self.occupy) == 3:
            self.occupy.pop(0)

        last = self.occupy[-1]
        section = self.model.sections[last[0]]
        if (last[1] == "forward" and section.next is None) or (last[1] == "reverse" and section.previous is None):
            self.occupy.append((last[0], NavigateModel.oppositeDirectionFrom(last[1])))
        self.listener.connect({"id": last[0]}, last[1])

def test_single_section():
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

