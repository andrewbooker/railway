
import threading
import sys
from datetime import datetime


class StatusComponent:
    def __init__(self, h):
        self.h = h

    def height(self):
        return self.h

    def setValue(self, v):
        pass

    def strValue(self):
        pass


class StatusRenderer:
    def __init__(self):
        self.components: list[StatusComponent] = []
        self.height = 0
        self.width = 100
        self.firstValueWritten = False
        self.lock = threading.Lock()

    def add(self, component: StatusComponent):
        self.height += component.height()
        self.components.append(component)
        return self

    def render(self):
        if self.lock.locked():
            return
        self.lock.acquire()
        if self.firstValueWritten:
            sys.stdout.write("\x1b[A" * (self.height + 1))
            sys.stdout.flush()

        for c in self.components:
            for s in c.strValue():
                if len(s) < self.width:
                    sys.stdout.write("%s%s\n\r" % (s, " " * (self.width - len(s))))
                else:
                    sys.stdout.write(s)

        sys.stdout.flush()
        self.lock.release()
        self.firstValueWritten = True


class TextStatusComponent(StatusComponent):
    def __init__(self, h):
        StatusComponent.__init__(self, h)
        self.v = []

    def setValue(self, v):
        t = datetime.now().strftime("%H%M%S.%f")
        self.v.append(f"{t} {v}")
        if len(self.v) > self.height():
            self.v.pop(0)

    def strValue(self):
        return self.v


class PowerStatusComponent(StatusComponent):
    scale = 100

    def __init__(self):
        StatusComponent.__init__(self, 3)
        self.v = 0

    def setValue(self, v):
        self.v = v

    def strValue(self):
        r = []
        for i in range(3):
            s = [
                "\033[92m%s\033[0m" % ("\u2589" * self.v),
                "\033[0;37m%s\033[0m" % ("\u2589" * (PowerStatusComponent.scale - self.v)),
                "\n\r"
            ]
            r.append("".join(s))
        return r


class PowerMonitor:
    def __init__(self):
        self.renderer = StatusRenderer()
        self.msg = TextStatusComponent(48)
        self.status = TextStatusComponent(1)
        self.power = PowerStatusComponent()
        self.renderer.add(self.status).add(self.power).add(self.msg)

    def _render(self):
        self.renderer.render()

    def setValue(self, value):
        self.power.setValue(value)
        self._render()

    def setMessage(self, m):
        self.msg.setValue(m)
        self._render()

    def setStatus(self, s):
        self.status.setValue(s)
        self._render()
