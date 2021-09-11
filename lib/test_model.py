
from model import *



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

outgoingPointsWithSidingLeft = """
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

def test_outgoing_points_as_complete_section():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))

    points = m.sections["p01"]
    assert points.__class__ == Points
    assert points.name == "the track"
    assert points.direction == ("RPi", 26)
    assert points.forwardUntil is None
    assert points.reverseUntil == ("RPi", 16)
    assert points.incoming is None
    assert points.next is None
    assert points.previous is None

    assert points.outgoing.detector == ("RPi", 17)
    assert points.outgoing.selector == ("RPi", 25)
    assert points.outgoing.left.next is None
    assert points.outgoing.left.previous is None
    assert points.outgoing.left.forwardUntil == ("RPi", 14)
    assert points.outgoing.left.reverseUntil is None
    assert points.outgoing.right.forwardUntil == ("RPi", 15)
    assert points.outgoing.right.reverseUntil is None
    assert points.outgoing.right.next is None
    assert points.outgoing.right.previous is None

def test_outgoing_points_with_siding():
    m = Model(outgoingPointsWithSidingLeft)

    siding = m.sections["s01"]
    assert siding.name == "siding"
    assert siding.next is None
    assert siding.previous == ("p01", "outgoing", "right")
    assert siding.direction == ("RPi", 27)
    assert siding.forwardUntil == ("RPi", 14)
    assert siding.reverseUntil is None

    points = m.sections["p01"]
    assert points.__class__ == Points
    assert points.name == "main"
    assert points.direction == ("RPi", 26)
    assert points.next is None
    assert points.previous is None
    assert points.forwardUntil is None
    assert points.reverseUntil == ("RPi", 17)
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

def test_simple_fork():
    m = Model(openLayout("example-layouts/simple-fork.json"))

    approach = m.sections["s01"]
    assert approach.name == "main branch"
    assert approach.direction == ("RPi", 23)
    assert approach.next == ("p01", "forward")
    assert approach.previous is None
    assert approach.forwardUntil is None
    assert approach.reverseUntil == ("RPi", 14)

    left = m.sections["s02"]
    assert left.name == "branch left"
    assert left.direction == ("RPi", 24)
    assert left.next is None
    assert left.previous == ("p01", "outgoing", "left")
    assert left.forwardUntil == ("RPi", 15)
    assert left.reverseUntil is None

#siding on the right
#incoming, left and right have previous but no next

