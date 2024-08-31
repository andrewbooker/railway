import json
from lib.routeIterator import PointsSelection
from lib.directionController import Direction


class Course:
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
        self.outgoing: Stage | None = None
        self.incoming: Stage | None = None


class Model:
    @staticmethod
    def portFrom(p):
        return p["bank"], p["port"]

    @staticmethod
    def _courseFrom(points, stage, selection):
        c = Course()
        spec = points[stage][selection]
        if "until" in spec:
            c.forwardUntil = Model.portFrom(spec["until"])
        if "id" in spec:
            direction = Direction.value_of(spec["direction"]) if "direction" in spec else Direction.Forward
            if stage == "outgoing":
                c.next = (spec["id"], direction)
            else:
                c.previous = (spec["id"], direction)
        return c

    @staticmethod
    def _nextSectionDirectionFrom(spec, direction: Direction):
        sd = spec[direction.value]
        if "params" in sd and len(sd["params"]) > 1:
            stage = sd["params"][0]
            direction = Direction.Reverse if stage == "outgoing" else Direction.Forward
            return sd["id"], direction, stage, PointsSelection.valueOf(sd["params"][1])
        return sd["id"], direction

    def _points_course_detection(self, termination):
        if termination is not None:
            self._register_detector({"bank": termination[0], "port": termination[1]})

    def _pointsStageFrom(self, points, stage):
        left = Model._courseFrom(points, stage, "left")
        right = Model._courseFrom(points, stage, "right")
        self._register_detector(points[stage]["detector"])
        self._points_course_detection(left.forwardUntil)  # not sure reverseUntil is needed in points
        self._points_course_detection(right.forwardUntil)
        return Stage(left, right, Model.portFrom(points[stage]["selector"]), Model.portFrom(points[stage]["detector"]))

    def __init__(self, m):
        js = json.loads(m)

        self.detection_ports = {}
        self.relay_ports = {}
        self.sections = {}
        for s in js:
            isPoints = "type" in s and s["type"] == "points"
            section = Points(s["name"]) if isPoints else Section(s["name"])
            section.direction = Model.portFrom(s["direction"])
            self._register_relay(s["direction"])

            if "next" in s and len(s["next"]) > 0:
                n = s["next"]
                if "forward" in n:
                    section.next = Model._nextSectionDirectionFrom(n, Direction.Forward)
                if "reverse" in n:
                    section.previous = Model._nextSectionDirectionFrom(n, Direction.Reverse)

            if "until" in s:
                u = s["until"]
                if "forward" in u:
                    forward_until = u["forward"]
                    section.forwardUntil = Model.portFrom(forward_until)
                    self._register_detector(forward_until)
                if "reverse" in u:
                    reverse_until = u["reverse"]
                    section.reverseUntil = Model.portFrom(reverse_until)
                    self._register_detector(reverse_until)

            if "outgoing" in s:
                section.outgoing = self._pointsStageFrom(s, "outgoing")
                section.next = section.outgoing
            if "incoming" in s:
                section.incoming = self._pointsStageFrom(s, "incoming")
                section.previous = section.incoming

            self.sections[s["id"]] = section

    def _register_detector(self, detector):
        self.detection_ports.setdefault(detector["bank"], set()).add(detector["port"])

    def _register_relay(self, relay):
        self.relay_ports.setdefault(relay["bank"], set()).add(relay["port"])

    def detectionPorts(self):
        return self.detection_ports

    def relayPorts(self):
        return self.relay_ports

    def sectionFrom(self, portId):
        bank, i = tuple(portId.split("_"))
        for sId, s in self.sections.items():
            if type(s) is Section and s.direction == (bank, int(i)):
                return {"sId": sId, "section": s}
        return None
