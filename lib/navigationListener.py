

class NavigationListener():
    def __init__(self, detectionListener, directionController, pointsController):
        self.detectionListener = detectionListener
        self.directionController = directionController
        self.pointsController = pointsController
        self.currentDirection = "forward"
        self.currentSection = None
        self.nextRequestor = None

    @staticmethod
    def portId(p):
        return "%s_%s" % (p["bank"], p["port"])

    def _set(self):
        self.detectionListener.clearCallback()

        if "type" in self.currentSection and self.currentSection["type"] == "points":
            self.directionController.set(NavigationListener.portId(self.currentSection["outgoing"]["direction"]), self.currentDirection)
            self.nextRequestor()
            return
        else:
            self.directionController.set(NavigationListener.portId(self.currentSection["direction"]), self.currentDirection)

        if "until" in self.currentSection:
            u = self.currentSection["until"]
            if self.currentDirection in u:
                d = u[self.currentDirection]
                self.detectionListener.setCallback(self.nextRequestor)
                self.detectionListener.setNextDetector(NavigationListener.portId(d), 1)

        if "next" in self.currentSection:
            n = self.currentSection["next"]
            if self.currentDirection in n and n[self.currentDirection]["id"][0] == "p":
                points = self.pointsController.fromId(n[self.currentDirection]["id"])
                stage = n[self.currentDirection]["params"][0]
                self.detectionListener.setCallback(self.nextRequestor)
                self.detectionListener.setNextDetector(NavigationListener.portId(points[stage]["detector"]), 0)


    def setNextRequestor(self, r):
        self.nextRequestor = r

    def changeDirection(self, to):
        self.currentDirection = to
        if "until" in self.currentSection:
            self._set()

    def moveTo(self, section):
        self.currentSection = section
        self._set()

    def setPointsTo(self, s, stage, p):
        self.detectionListener.waitFor(NavigationListener.portId(p[stage]["detector"]), 1)
        self.pointsController.set(p["id"], stage, s)

    def waitToSetPointsTo(self, s, stage, p):
        self.detectionListener.setCallback(self.nextRequestor)
        self.detectionListener.setNextDetector(NavigationListener.portId(p[stage]["detector"]), 0)
        self.pointsController.set(p["id"], stage, s)
