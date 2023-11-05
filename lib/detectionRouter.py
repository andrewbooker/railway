
class AndThen:
    def __init__(self):
        self.m = None

    def then(self, m):
        self.m = m

    def canExec(self):
        return self.m is not None

    def exec(self):
        self.m()


class DetectionListener:
    def setNextDetector(self, d, v, description):
        pass

    def waitFor(self, d, state, description):
        pass


class DetectionRouter(DetectionListener):
    def __init__(self):
        self.callback = None
        self.awaiting = {}

    def setCallback(self, c):
        cb = AndThen()
        cb.then(c)
        self.callback = cb

    def receiveUpdate(self, portId, value):
        k = (portId, value)
        if k not in self.awaiting:
            return

        (description, cb) = self.awaiting[k]
        del self.awaiting[k]
        if cb is not None and cb.canExec():
            cb.exec()
            return
        if self.callback is not None:
            self.callback.exec()

    def setNextDetector(self, p, v, description):
        self.awaiting[(p, v)] = (description, self.callback)

    def waitFor(self, p, v, description):
        cb = AndThen()
        self.awaiting[(p, v)] = (description, cb)
        return cb
