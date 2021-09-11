import json

class Course():
    def __init__(self):
        self.next = None
        self.previous = None
        self.forwardUntil = None
        self.reverseUntil = None

class Section(Course):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.direction = None

class Stage():
    def __init__(self, l: Course, r: Course, selector, detector):
        self.left = l
        self.right = r
        self.selector = selector
        self.detector = detector

class Points(Section):
    def __init__(self, name):
        super().__init__(name)
        self.outgoing: Stage = None
        self.incoming: Stage = None

class Model():
    @staticmethod
    def portFrom(p):
        return (p["bank"], p["port"])

    @staticmethod
    def _courseFrom(spec):
        c = Course()
        if "until" in spec:
            c.forwardUntil = Model.portFrom(spec["until"])
        if "id" in spec:
            c.next = (spec["id"], spec["direction"])
        return c

    def __init__(self, m):
        js = json.loads(m)

        self.sections = {}
        for s in js:
            isPoints = "type" in s and s["type"] == "points"
            section = Points(s["name"]) if isPoints else Section(s["name"])
            section.direction = Model.portFrom(s["direction"])

            if "next" in s and len(s["next"]) > 0:
                n = s["next"]
                if "forward" in n:
                    section.next = (n["forward"]["id"], "forward")
                if "reverse" in n:
                    section.previous = (n["reverse"]["id"], "reverse")

            if "until" in s:
                u = s["until"]
                if "forward" in u:
                    section.forwardUntil = Model.portFrom(u["forward"])
                if "reverse" in u:
                    section.reverseUntil = Model.portFrom(u["reverse"])

            if "outgoing" in s:
                o = s["outgoing"]
                l = o["left"]
                r = o["right"]
                left = Model._courseFrom(o["left"])
                right = Model._courseFrom(o["right"])
                section.outgoing = Stage(left, right, Model.portFrom(o["selector"]), Model.portFrom(o["detector"]))

            self.sections[s["id"]] = section
