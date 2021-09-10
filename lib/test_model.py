

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
        self.outgoing = None # or a Stage
        self.incoming = None # or a Stage

class Model():
    def __init__(self, m):
        js = json.loads(m)
        
        self.sections = {}
        for s in js:
            isPoints = "type" in s and s["type"] == "points"
            section = Points(s["name"]) if isPoints else Section(s["name"])
            d = s["direction"]
            section.direction = (d["bank"], d["port"])

            if "next" in s and len(s["next"]) > 0:
                n = s["next"]
                if "forward" in n:
                    section.next = (n["forward"]["id"], "forward")
                if "reverse" in n:
                    section.previous = (n["reverse"]["id"], "reverse")

            if "until" in s:
                u = s["until"]
                if "forward" in u:
                    uf = u["forward"]
                    section.forwardUntil = (uf["bank"], uf["port"])
                if "reverse" in u:
                    uf = u["reverse"]
                    section.reverseUntil = (uf["bank"], uf["port"])

            if "outgoing" in s:
                o = s["outgoing"]
                l = o["left"]
                r = o["right"]
                left = Course()
                if "until" in l:
                    left.forwardUntil = (l["until"]["bank"], l["until"]["port"])
                right = Course()
                if "id" in r:
                    right.next = (r["id"], r["direction"])
                det = o["detector"]
                sel = o["selector"]
                section.outgoing = Stage(left, right, (sel["bank"], sel["port"]), (det["bank"], det["port"]))

            self.sections[s["id"]] = section


def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


def test_single_section():
    m = Model(openLayout("example-layouts/shuttle.json"))

    section = m.sections["s01"]
    assert section.name == "shuttle track"
    assert section.next is None
    assert section.previous is None
    assert section.direction == ("RPi", 23)
    assert section.forwardUntil == ("RPi", 14)
    assert section.reverseUntil == ("RPi", 15)

loop = """
[
    {
        "id": "s01",
        "name": "loop",
        "direction": {"bank": "RPi", "port": 16},
        "next": {
            "forward": {"id": "s01"},
            "reverse": {"id": "s01"}
        }
    }
]
"""

def test_loop_has_self_referencing_next_and_previous_with_required_directions():
    m = Model(loop)

    section = m.sections["s01"]
    assert section.name == "loop"
    assert section.next == ("s01", "forward")
    assert section.previous == ("s01", "reverse")
    assert section.direction == ("RPi", 16)
    assert section.forwardUntil is None
    assert section.reverseUntil is None

outgoingPointsWithASiding = """
[
    {
        "id": "p01",
        "name": "main",
        "type": "points",
        "direction": {
		    "bank": "RPi",
		    "port": 26
	    },
        "until": {
            "reverse": {
	            "bank": "RPi",
	            "port": 17
            }
        },
        "outgoing": {
            "left": {
                "until": {
		            "bank": "RPi",
		            "port": 18
	            }
            },
            "right": {
                "id": "s01",
                "direction": "forward"
            },
            "selector": {
                "bank": "RPi",
                "port": 25
            },
		    "detector": {
			    "bank": "RPi",
			    "port": 15
		    }
        }
    },
    {
        "id": "s01",
        "name": "siding",
		"direction": {
			"bank": "RPi",
			"port": 27
		},
        "next": {
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "right"]
            }
        },
        "until": {
            "forward": {
			    "bank": "RPi",
			    "port": 14
		    }
        }
    }
]
"""

def test_outgoing_points_with_siding():
    m = Model(outgoingPointsWithASiding)

    siding = m.sections["s01"]
    assert siding.name == "siding"
    assert siding.next is None
    assert siding.previous == ("p01", "reverse")
    assert siding.direction == ("RPi", 27)
    assert siding.forwardUntil == ("RPi", 14)
    assert siding.reverseUntil is None

    points = m.sections["p01"]
    assert points.name == "main"
    assert points.direction == ("RPi", 26)
    assert points.forwardUntil is None
    assert points.reverseUntil == ("RPi", 17)
    assert points.__class__.__name__ == "Points"
    assert points.incoming is None
    assert points.outgoing.left.next is None
    assert points.outgoing.left.previous is None
    assert points.outgoing.left.reverseUntil is None
    assert points.outgoing.left.forwardUntil == ("RPi", 18)
    assert points.outgoing.right.next == ("s01", "forward")
    assert points.outgoing.right.previous is None
    assert points.outgoing.right.forwardUntil is None
    assert points.outgoing.right.reverseUntil is None
    assert points.outgoing.detector == ("RPi", 15)
    assert points.outgoing.selector == ("RPi", 25)

