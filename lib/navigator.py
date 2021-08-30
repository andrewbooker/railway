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
        self.history.append((s["id"], self.direction))
        self.listener.moveTo(s)

    @staticmethod
    def _check(section, pointsId, direction):
        if direction not in section:
            return None
        sp = section[direction]
        if len(sp["params"]) == 0 and sp["id"] == pointsId:
            return section
        return None

    def _afterConvergence(self, atPointsId):
        for s in self.layout:
            next = s["next"]
            if Journey._check(next, atPointsId, "forward") is not None:
                return (s, "forward")
            if Journey._check(next, atPointsId, "reverse") is not None:
                return (s, "reverse")

    def start(self):
        self._at(self.layout[0])

    def changeDirection(self):
        self.direction = "forward" if self.direction == "reverse" else "reverse"
        self.history.append((self.section["id"], self.direction))
        self.listener.changeDirection(self.direction)

    def nextStage(self):
        if "next" not in self.section:
            if "type" in self.section and self.section["type"] == "points":
                points = self.section
                previousSection = self._find(self.history[-2][0])
                approachingDivergence = len(previousSection["next"][self.direction]["params"]) == 0
                if approachingDivergence:
                    choice = self.selectPoints()
                    self.listener.setPointsTo(choice, points)
                    self.history.append(("points selection", choice))
                    nextDirection = points[choice]["direction"] if "direction" in points[choice] else "forward"
                    if nextDirection != self.direction:
                        self.changeDirection()
                    self._at(self._find(points[choice]["id"]))
                else:
                    expectedPoints = previousSection["next"][self.direction]["params"][0]
                    self.listener.waitToSetPointsTo(expectedPoints, points)
                    (nextSection, nextDirection) = self._afterConvergence(points["id"])
                    if nextDirection == self.direction:
                        self.changeDirection()
                    self.history.append(("points condition", expectedPoints))
                    self._at(nextSection)
        else:
            options = self.section["next"]
            if self.direction in options:
                self._at(self._find(options[self.direction]["id"]))
            else:
                self.changeDirection()
