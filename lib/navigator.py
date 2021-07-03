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
        print("now on", s["name"])

    def changeDirection(self):
        self.direction = "forward" if self.direction == "reverse" else "reverse"
        self.history.append((self.section["id"], self.direction))

    def nextStage(self):
        print("from", self.section["name"])
        if "next" not in self.section:
            points = self.section
            if points["id"][0] == "p":
                if self.direction == "forward":
                    choice = points["param"] if "param" in points else self.selectPoints()
                    print("choosing", choice)
                    self._at(self._find(points[choice]["id"]))
                else:
                    expectedPoints = "left" if points["left"]["id"] == self.history[-2] else "right"
                    print("points expected to be", expectedPoints)
                    for s in self.layout["sections"]:
                        if "forward" in s["next"] and s["next"]["forward"]["id"] == points["id"]:
                            self._at(s)
        else:
            options = self.section["next"]
            if self.direction in options:
                self._at(self._find(options[self.direction]["id"]))
            else:
                self.changeDirection()
                print("changing direction to", self.direction)
