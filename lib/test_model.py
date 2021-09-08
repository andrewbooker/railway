

import json

class Section():
    def __init__(self, name):
        self.name = name
        self.next = None
        self.previous = None
        self.direction = None
        self.forwardUntil = None
        self.reverseUntil = None

class Model():
    def __init__(self, m):
        js = json.loads(m)
        
        self.sections = {}
        for s in js:
            section = Section(s["name"])
            d = s["direction"]
            section.direction = (d["bank"], d["port"])

            if len(s["next"]) > 0:
                n = s["next"]
                if "forward" in n:
                    section.next = (n["forward"]["id"], "forward")
                if "reverse" in n:
                    section.previous = (n["forward"]["id"], "reverse")

            if "until" in s:
                u = s["until"]
                if "forward" in u:
                    uf = u["forward"]
                    section.forwardUntil = (uf["bank"], uf["port"])
                if "reverse" in u:
                    uf = u["reverse"]
                    section.reverseUntil = (uf["bank"], uf["port"])
            self.sections[s["id"]] = section


def openLayout(fileName):
    with open(fileName, "r") as layoutSpec:
        return layoutSpec.read()


def test_single_section():
    m = Model(openLayout("example-layouts/shuttle.json"))

    section = m.sections["s01"]
    assert section.name == "shuttle track"
    assert section.next == None
    assert section.previous == None
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
    assert section.forwardUntil == None
    assert section.reverseUntil == None



