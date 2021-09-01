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

    def start(self):
        self._at(self.layout[0])

    def changeDirection(self):
        self.direction = "forward" if self.direction == "reverse" else "reverse"
        self.listener.connect(self.section, self.direction)

    def nextStage(self):
        if "next" not in self.section:
            if "type" in self.section and self.section["type"] == "points":
                points = self.section
                previousSection = self._find(self.history[-2])
                approachingDivergence = len(previousSection["next"][self.direction]["params"]) < 2
                stage = previousSection["next"][self.direction]["params"][0] if len(previousSection["next"][self.direction]["params"]) > 0 else "outgoing"
                if approachingDivergence:
                    choice = self.selectPoints()
                    self.listener.setPointsTo(choice, stage, points)
                    nextDirection = points[stage][choice]["direction"] if "direction" in points[stage][choice] else "forward"
                    if nextDirection != self.direction:
                        self.changeDirection()
                    self._at(self._find(points[stage][choice]["id"]))
                else:
                    expectedPoints = previousSection["next"][self.direction]["params"][1]
                    self.listener.waitToSetPointsTo(expectedPoints, stage, points)
                    (nextSection, nextDirection, nextPointsStage) = self._afterConvergence(points["id"], stage)
                    if nextPointsStage is not None:
                        #copied from above, changed stage to nextPointsStage:
                        choice = self.selectPoints()
                        self.listener.setPointsTo(choice, nextPointsStage, points)
                        nextDirection = points[nextPointsStage][choice]["direction"] if "direction" in points[nextPointsStage][choice] else "forward"
                        if nextDirection != self.direction:
                            self.changeDirection()
                        self._at(self._find(points[nextPointsStage][choice]["id"]))
                    else:
                        if nextDirection == self.direction:
                            self.changeDirection()
                        self._at(nextSection)

        else:
            options = self.section["next"]
            if self.direction in options:
                self._at(self._find(options[self.direction]["id"]))
            else:
                self.changeDirection()
