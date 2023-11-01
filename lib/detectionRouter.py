from routeNavigator import DetectionListener


class AndThen:
    def __init__(self):
        self.m = None

    def then(self, m):
        self.m = m

    def canExec(self):
        return self.m is not None

    def exec(self):
        self.m()


class DetectionRouter(DetectionListener):
    def __init__(self):
        self.callback = None
        self.awaiting = {}

    def setCallback(self, c):
        self.callback = c

    def receiveUpdate(self, portId, value):
        k = (portId, value)
        if k not in self.awaiting:
            return

        (description, cb) = self.awaiting[k]
        del self.awaiting[k]
        if cb.canExec():
            cb.exec()
            return
        if self.callback is not None:
            self.callback()

    def setNextDetector(self, p, v, description):
        self.awaiting[(p, v)] = (description, self.callback)

    def waitFor(self, p, v, description):
        cb = AndThen()
        self.awaiting[(p, v)] = (description, cb)
        return cb
