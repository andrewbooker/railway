
import readchar
import threading

class Cmd():
    def __init__(self, callback):
        self.callback = callback

    def start(self, shouldStop):
        while not shouldStop.is_set():
            c = readchar.readchar()
            if ord(c) in [3, 27, 113]: #ctrl+C, esc or q
                shouldStop.set()
            else:
                self.callback(c)

shouldStop = threading.Event()