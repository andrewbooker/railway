

import json

class Section():
    def __init__(self, name):
        self.name = name
        self.next = None
        self.previous = None

class Model():
    def __init__(self, m):
        js = json.loads(m)
        
        self.sections = {}
        for s in js:
            section = Section(s["name"])
            if len(s["next"]) > 0:
                n = s["next"]
                if "forward" in n:
                    section.next = (n["forward"]["id"], "forward")
                if "reverse" in n:
                    section.previous = (n["forward"]["id"], "reverse")
            self.sections[s["id"]] = section


straightLine = """
[
    {
        "id": "s01",
        "name": "shuttle", 
        "next": {}
    }
]
"""

def test_single_section():
    m = Model(straightLine)

    section = m.sections["s01"]
    assert section.name == "shuttle"
    assert section.next == None
    assert section.previous == None

loop = """
[
    {
        "id": "s01",
        "name": "loop",
        "next": {
            "forward": {"id": "s01"},
            "reverse": {"id": "s01"}
        }
    }
]
"""

def test_loop_has_self_referencing_next_and_previous():
    m = Model(loop)

    section = m.sections["s01"]
    assert section.name == "loop"
    assert section.next == ("s01", "forward")
    assert section.previous == ("s01", "reverse")
