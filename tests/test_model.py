from lib.model import *


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
    assert section.forwardUntil == ("arduino", 52)
    assert section.reverseUntil == ("arduino", 53)

    assert m.detectionPorts()["arduino"] == {52, 53}
    assert m.relayPorts()["RPi"] == {23}


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
    assert section.next == ("s01", Direction.Forward)
    assert section.previous == ("s01", Direction.Reverse)
    assert section.direction == ("RPi", 16)
    assert section.forwardUntil is None
    assert section.reverseUntil is None
    assert m.detectionPorts() == dict()
    assert m.relayPorts()["RPi"] == {16}


def test_outgoing_points_as_complete_section():
    m = Model(openLayout("example-layouts/points-as-large-y.json"))

    points = m.sections["p01"]
    assert points.__class__ == Points
    assert points.name == "the track"
    assert points.direction == ("RPi", 26)
    assert points.forwardUntil is None
    assert points.reverseUntil == ("RPi", 16)
    assert points.incoming is None
    assert points.next == points.outgoing
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

    assert m.detectionPorts()["RPi"] == {14, 15, 16, 17}
    assert m.relayPorts()["RPi"] == {26}


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
                "id": "s01",
                "direction": "forward"
            },
            "right": {
                "until": {
		            "bank": "RPi",
		            "port": 18
	            }
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
                "params": ["outgoing", "left"]
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


def test_outgoing_points_with_siding_left():
    m = Model(outgoingPointsWithSidingLeft)

    siding = m.sections["s01"]
    assert siding.name == "siding"
    assert siding.next is None
    assert siding.previous == ("p01", Direction.Reverse, "outgoing", PointsSelection.Left)
    assert siding.direction == ("RPi", 27)
    assert siding.forwardUntil == ("RPi", 14)
    assert siding.reverseUntil is None

    points = m.sections["p01"]
    assert points.__class__ == Points
    assert points.name == "main"
    assert points.direction == ("RPi", 26)
    assert points.next == points.outgoing
    assert points.previous is None
    assert points.forwardUntil is None
    assert points.reverseUntil == ("RPi", 17)
    assert points.incoming is None
    assert points.outgoing.left.next == ("s01", Direction.Forward)
    assert points.outgoing.left.previous is None
    assert points.outgoing.left.reverseUntil is None
    assert points.outgoing.left.forwardUntil is None
    assert points.outgoing.right.next is None
    assert points.outgoing.right.previous is None
    assert points.outgoing.right.forwardUntil == ("RPi", 18)
    assert points.outgoing.right.reverseUntil is None
    assert points.outgoing.detector == ("RPi", 15)
    assert points.outgoing.selector == ("RPi", 25)

    assert m.relayPorts()["RPi"] == {26, 27}


def test_simple_fork():
    m = Model(openLayout("example-layouts/simple-fork.json"))

    approach = m.sections["s01"]
    assert approach.name == "main branch"
    assert approach.direction == ("RPi", 23)
    assert approach.next == ("p01", Direction.Forward)
    assert approach.previous is None
    assert approach.forwardUntil is None
    assert approach.reverseUntil == ("RPi", 14)

    left = m.sections["s02"]
    assert left.name == "branch left"
    assert left.direction == ("RPi", 24)
    assert left.next is None
    assert left.previous == ("p01", Direction.Reverse, "outgoing", PointsSelection.Left)
    assert left.forwardUntil == ("RPi", 15)
    assert left.reverseUntil is None

    right = m.sections["s03"]
    assert right.name == "branch right"
    assert right.direction == ("RPi", 25)
    assert right.next is None
    assert right.previous == ("p01", Direction.Reverse, "outgoing", PointsSelection.Right)
    assert right.forwardUntil == ("RPi", 16)
    assert right.reverseUntil is None

    points = m.sections["p01"]
    assert points.__class__ == Points
    assert points.name == "branching points"
    assert points.direction == ("RPi", 26)
    assert points.next == points.outgoing
    assert points.previous == ("s01", Direction.Reverse)
    assert points.forwardUntil is None
    assert points.forwardUntil is None
    assert points.incoming is None
    assert points.outgoing.left.next == ("s02", Direction.Forward)
    assert points.outgoing.left.previous is None
    assert points.outgoing.left.reverseUntil is None
    assert points.outgoing.left.forwardUntil is None
    assert points.outgoing.right.next == ("s03", Direction.Forward)
    assert points.outgoing.right.previous is None
    assert points.outgoing.right.forwardUntil is None
    assert points.outgoing.right.reverseUntil is None
    assert points.outgoing.detector == ("RPi", 17)
    assert points.outgoing.selector == ("RPi", 27)

    assert m.detectionPorts()["RPi"] == {14, 15, 16, 17}
    assert m.relayPorts()["RPi"] == {23, 24, 25, 26}


incomingPointsWithSidingRight = """
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
            "forward": {
	            "bank": "RPi",
	            "port": 17
            }
        },
        "incoming": {
            "left": {
                "until": {
		            "bank": "RPi",
		            "port": 18
	            }
            },
            "right": {
                "id": "s01",
                "direction": "reverse"
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
            "forward": {
                "id": "p01",
                "params": ["incoming", "right"]
            }
        },
        "until": {
            "reverse": {
			    "bank": "RPi",
			    "port": 14
		    }
        }
    }
]
"""


def test_incoming_points_with_siding_right():
    m = Model(incomingPointsWithSidingRight)

    siding = m.sections["s01"]
    assert siding.name == "siding"
    assert siding.next == ("p01", Direction.Forward, "incoming", PointsSelection.Right)
    assert siding.previous is None
    assert siding.direction == ("RPi", 27)
    assert siding.forwardUntil is None
    assert siding.reverseUntil == ("RPi", 14)

    points = m.sections["p01"]
    assert points.__class__ == Points
    assert points.name == "main"
    assert points.direction == ("RPi", 26)
    assert points.next is None
    assert points.previous == points.incoming
    assert points.forwardUntil == ("RPi", 17)
    assert points.reverseUntil is None
    assert points.outgoing is None
    assert points.incoming.left.next is None
    assert points.incoming.left.previous is None
    assert points.incoming.left.reverseUntil is None
    assert points.incoming.left.forwardUntil == ("RPi", 18)
    assert points.incoming.right.previous == ("s01", Direction.Reverse)
    assert points.incoming.right.next is None
    assert points.incoming.right.forwardUntil is None
    assert points.incoming.right.reverseUntil is None
    assert points.incoming.detector == ("RPi", 15)
    assert points.incoming.selector == ("RPi", 25)

    assert m.relayPorts()["RPi"] == {26, 27}


def test_return_loops_back_to_back():
    m = Model(openLayout("example-layouts/return-loops-back-to-back.json"))

    loop1 = m.sections["r01"]
    assert loop1.next == ("p01", Direction.Reverse, "outgoing", PointsSelection.Right)
    assert loop1.previous == ("p01", Direction.Reverse, "outgoing", PointsSelection.Left)
    assert loop1.forwardUntil is None
    assert loop1.reverseUntil is None

    loop2 = m.sections["r02"]
    assert loop2.next == ("p01", Direction.Forward, "incoming", PointsSelection.Right)
    assert loop2.previous == ("p01", Direction.Forward, "incoming", PointsSelection.Left)
    assert loop2.forwardUntil is None
    assert loop2.reverseUntil is None

    points = m.sections["p01"]
    assert points.forwardUntil is None
    assert points.reverseUntil is None
    assert points.next == points.outgoing
    assert points.previous == points.incoming
    assert points.outgoing.left.previous is None
    assert points.outgoing.left.next == ("r01", Direction.Forward)
    assert points.outgoing.right.previous is None
    assert points.outgoing.right.next == ("r01", Direction.Reverse)
    assert points.outgoing.detector == ("RPi", 15)
    assert points.outgoing.selector == ("RPi", 25)
    assert points.incoming.detector == ("RPi", 16)
    assert points.incoming.selector == ("RPi", 27)
    assert points.incoming.left.previous == ("r02", Direction.Forward)
    assert points.incoming.left.next is None
    assert points.incoming.right.previous == ("r02", Direction.Reverse)
    assert points.incoming.right.next is None

    assert m.relayPorts()["RPi"] == {23, 24, 26}


def test_return_loop():
    m = Model(openLayout("example-layouts/return-loop.json"))

    s = m.sections["s01"]
    assert s.name == "main branch"
    assert s.direction == ("RPi", 23)
    assert s.next == ("p01", Direction.Forward)
    assert s.previous is None
    assert s.forwardUntil is None
    assert s.reverseUntil == ("RPi", 14)

    loop = m.sections["r01"]
    assert loop.direction == ("RPi", 24)
    assert loop.next == ("p01", Direction.Reverse, "outgoing", PointsSelection.Right)
    assert loop.previous == ("p01", Direction.Reverse, "outgoing", PointsSelection.Left)
    assert loop.forwardUntil is None
    assert loop.reverseUntil is None

    points = m.sections["p01"]
    assert points.direction == ("RPi", 26)
    assert points.forwardUntil is None
    assert points.reverseUntil is None
    assert points.next == points.outgoing
    assert points.previous == ("s01", Direction.Reverse)
    assert points.outgoing.left.previous is None
    assert points.outgoing.left.next == ("r01", Direction.Forward)
    assert points.outgoing.right.previous is None
    assert points.outgoing.right.next == ("r01", Direction.Reverse)
    assert points.outgoing.detector == ("RPi", 15)
    assert points.outgoing.selector == ("RPi", 25)
    assert points.incoming is None


def test_opposing_points_loop():
    m = Model(openLayout("example-layouts/opposing-points-loop.json"))

    out = m.sections["p01"]
    assert out.next == out.outgoing
    assert out.previous == ("p02", Direction.Forward, "incoming", PointsSelection.Left)

    inc = m.sections["p02"]
    assert inc.previous == inc.incoming
    assert inc.next == ("p01", Direction.Reverse, "outgoing", PointsSelection.Left)
