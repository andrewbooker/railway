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
    def __init__(self, left: Course, right: Course, selector, detector):
        self.left = left
        self.right = right
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
            direction = spec["direction"] if "direction" in spec else "forward"
            c.next = (spec["id"], direction)
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
                    fw = n["forward"]
                    if "params" in fw:
                        section.next = (fw["id"], fw["params"][0], fw["params"][1])
                    else:
                        section.next = (fw["id"], "forward")
                if "reverse" in n:
                    rv = n["reverse"]
                    if "params" in rv:
                        section.previous = (rv["id"], rv["params"][0], rv["params"][1])
                    else:
                        section.previous = (rv["id"], "reverse")

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

            if "incoming" in s:
                stage = s["incoming"]
                l = stage["left"]
                r = stage["right"]
                left = Model._courseFrom(stage["left"])
                right = Model._courseFrom(stage["right"])
                section.incoming = Stage(left, right, Model.portFrom(stage["selector"]), Model.portFrom(stage["detector"]))

            self.sections[s["id"]] = section
