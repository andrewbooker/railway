
class Direction():
    def __init__(self, port):
        self.port = port

    def set(self, isForwards):
        self.port.set(0 if isForwards else 1)
