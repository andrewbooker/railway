import json
from random import randint

class Journey():
    def __init__(self, layoutStr):
        self.layout = json.loads(layoutStr)
        self.direction = "forward"
        self.history = []
        self._at(self.layout["sections"][0])
        self.selectPoints = lambda: "left" if (randint(0, 1) > 0) else "right"

    def _find(self, id):
        if "points" in self.layout:
            for p in self.layout["points"]:
                if p["id"] == id:
                    return p
        for s in self.layout["sections"]:
            if s["id"] == id:
                return s
        return None

    def _at(self, s):
        self.section = s
        self.history.append((s["id"], self.direction))
        print("now on", s["name"], self.direction)

    def changeDirection(self):
        self.direction = "forward" if self.direction == "reverse" else "reverse"
        self.history.append((self.section["id"], self.direction))
        print("changing direction to", self.direction)

    def nextStage(self):
        print("from", self.section["name"])
        if "next" not in self.section:
            if self.section["id"][0] == "p":
                points = self.section
                previousSection = self._find(self.history[-2][0])
                approachingToDiverge = "param" not in previousSection["next"][self.direction]
                if approachingToDiverge:
                    choice = self.selectPoints()
                    print("heading", choice)
                    self.history.append(("points selection", choice))
                    self._at(self._find(points[choice]["id"]))
                else:
                    expectedPoints = previousSection["next"][self.direction]["param"]
                    print("expecting", expectedPoints)
                    if "direction" in points[expectedPoints] and self.direction not in points[expectedPoints]["direction"]:
                        self.changeDirection()
                    self.history.append(("points condition", expectedPoints))
                    for s in self.layout["sections"]:
                        if "forward" in s["next"] and "param" not in s["next"]["forward"] and s["next"]["forward"]["id"] == points["id"]:
                            self._at(s)
        else:
            options = self.section["next"]
            if self.direction in options:
                self._at(self._find(options[self.direction]["id"]))
            else:
                self.changeDirection()
