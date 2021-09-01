import json
from random import randint

class Journey():
    def __init__(self, layoutStr, listener):
        self.listener = listener
        self.layout = json.loads(layoutStr)
        self.direction = "forward"
        self.history = []
        self.section = None
        self.selectPoints = lambda: "left" if (randint(0, 1) > 0) else "right"

    def _find(self, id):
        for s in self.layout:
            if s["id"] == id:
                return s
        return None

    def _at(self, s):
        self.section = s
        self.history.append(s["id"])
        self.listener.connect(s, self.direction)

    @staticmethod
    def _check(section, pointsId, direction):
        if direction not in section:
            return None
        sp = section[direction]
        if len(sp["params"]) < 2 and sp["id"] == pointsId:
            return section
        return None

    def _afterConvergence(self, atPointsId, stage):
        points = self._find(atPointsId)
        nextPointsStage = "incoming" if stage == "outgoing" else "outgoing"
        if nextPointsStage in points:
            return (points, self.direction, nextPointsStage)

        for s in self.layout:
            next = s["next"] # note this works only if regular sections with "next" elements are all specified before the points
            if Journey._check(next, atPointsId, "forward") is not None:
                return (s, "forward", None)
            if Journey._check(next, atPointsId, "reverse") is not None:
                return (s, "reverse", None)

    def _approachDivergence(self, points, stage):
        choice = self.selectPoints()
        self.listener.setPointsTo(choice, stage, points)
        nextDirection = points[stage][choice]["direction"] if "direction" in points[stage][choice] else "forward"
        if nextDirection != self.direction:
            self.direction = nextDirection
        self._at(self._find(points[stage][choice]["id"]))

    def _traversePoints(self, spec):
        points = self.section
        approachingDivergence = len(spec["params"]) < 2
        stage = spec["params"][0] if len(spec["params"]) > 0 else "outgoing"
        if approachingDivergence:
            self._approachDivergence(points, stage)
        else:
            expectedPoints = spec["params"][1]
            self.listener.waitToSetPointsTo(expectedPoints, stage, points)
            (nextSection, nextDirection, nextPointsStage) = self._afterConvergence(points["id"], stage)
            if nextPointsStage is not None:
                self._approachDivergence(points, nextPointsStage)
            else:
                if nextDirection == self.direction:
                    #travel in the correct direction down the points
                    self.changeDirection()
                    self.listener.connect(self.section, self.direction)
                # proceed to next section
                self._at(nextSection)

    def start(self):
        self._at(self.layout[0])

    def changeDirection(self):
        self.direction = "forward" if self.direction == "reverse" else "reverse"

    def nextStage(self):
        if "next" in self.section:
            next = self.section["next"]
            if self.direction in next:
                nextSection = self._find(next[self.direction]["id"])
                self._at(nextSection)
            else:
                #end of the line
                self.changeDirection()
                self.listener.connect(self.section, self.direction)
        elif "type" in self.section and self.section["type"] == "points":
            previousSection = self._find(self.history[-2])
            self._traversePoints(previousSection["next"][self.direction])
