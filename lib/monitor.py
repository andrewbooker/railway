
import threading
import sys

class PowerMonitor():
    def __init__(self):
        self.scale = 100
        self.height = 3
        self.msg = ""
        self.bar = 0
        self.firstValueWritten = False
        self.lock = threading.Lock()

    def _render(self):
        if self.lock.locked():
            return
        self.lock.acquire()
        fill = self.scale - self.bar

        if self.firstValueWritten:
            sys.stdout.write("\x1b[A" * (self.height + 1))
            sys.stdout.flush()
        else:
            self.firstValueWritten = True

        sys.stdout.write("%s%s\n\r" % (self.msg, " " * (self.scale - len(self.msg))))
        for h in range(self.height):
            sys.stdout.write("\033[92m%s\033[0m" % ("\u2589" * self.bar))
            sys.stdout.write("\033[0;37m%s\033[0m" % ("\u2589" * fill))
            sys.stdout.write("\n\r")

        sys.stdout.flush()
        self.lock.release()

    def setValue(self, value):
        self.bar = value
        self._render()

    def setMessage(self, m):
        self.msg = m
        self._render()
