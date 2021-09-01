 
from navigator import Journey


class InertListener():
    def __init__(self):
        pass

    def connect(self, section, direction):
        pass

    def setPointsTo(self, s, st, p):
        pass

    def waitToSetPointsTo(self, s, st, p):
        pass

listener = InertListener()
straightLine = "[{\"id\":\"s1\",\"name\":\"shuttle\",\"next\":{}}]"

def test_straight_line_track_at_start():
    journey = Journey(straightLine, listener)
    journey.start()
    assert journey.history == [("s1", "forward")]

def test_straight_line_track_after_one_move():
    journey = Journey(straightLine, listener)
    journey.start()
    journey.nextStage()
    assert journey.history == [("s1", "forward"),("s1", "reverse")]

def test_straight_line_track_after_multiple_moves():
    journey = Journey(straightLine, listener)
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s1", "forward"),("s1", "reverse"),("s1", "forward"),("s1", "reverse"),("s1", "forward")]


loop = "[{\"id\":\"s01\",\"name\":\"loop\",\"next\":{\"forward\":{\"id\":\"s01\"},\"reverse\":{\"id\":\"s01\"}}}]"

def test_loop_at_start():
    journey = Journey(loop, listener)
    journey.start()
    assert journey.history == [("s01", "forward")]

def test_loop_after_multiple_moves():
    journey = Journey(loop, listener)
    journey.start()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s01", "forward"),("s01", "forward"),("s01", "forward")]

def test_loop_after_change_of_direction():
    journey = Journey(loop, listener)
    journey.start()
    journey.nextStage()
    journey.changeDirection()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s01", "forward"),("s01", "forward"),("s01", "reverse"),("s01", "reverse"),("s01", "reverse")]


loopWithSiding = """
[
    {
        "id": "s01",
        "name": "main loop",
        "next": {
            "forward": {
                "id": "p01",
                "params": []
            },
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "right"]
            }
        }
    },
    {
        "id": "s02",
        "name": "branch siding",
        "next": {
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "left"]
            }
        }
    },
    {
        "id": "p01",
        "type": "points",
        "name": "branch siding points",
        "outgoing": {
            "left": {
                "id": "s02"
            },
            "right": {
                "id": "s01"
            }
        }
    }
]
"""

def test_loop_with_siding_points_right():
    journey = Journey(loopWithSiding, listener)
    journey.start()
    journey.selectPoints = lambda: "right"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("s01", "forward"),
        ("p01", "forward")]
        
def test_loop_with_siding_points_right_in_reverse():
    journey = Journey(loopWithSiding, listener)
    journey.start()
    journey.selectPoints = lambda: "right"
    journey.nextStage()
    journey.direction = "reverse"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points condition", "right"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("outgoing points condition", "right"),
        ("s01", "reverse")]

def test_loop_with_siding_points_left():
    journey = Journey(loopWithSiding, listener)
    journey.start()
    journey.selectPoints = lambda: "left"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("s02", "forward"),
        ("s02", "reverse"),
        ("p01", "reverse"),
        ("outgoing points condition", "left"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("outgoing points condition", "right"),
        ("s01", "reverse")]
    
returnLoop = """
[
    {
        "id": "s01",
        "name": "main branch",
        "next": {
            "forward": {
                "id": "p01",
                "params": []
            }
        }
    },
    {
        "id": "r01",
        "name": "return loop",
        "next": {
            "forward": {
                "id": "p01",
                "params": ["outgoing", "right"]
            },
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "left"]
            }
        }
    },
    {
        "id": "p01",
        "type": "points",
        "name": "return loop points",
        "outgoing": {
            "left": {
                "id": "r01"
            },
            "right": {
                "id": "r01",
                "direction": "reverse"
            }
        }
    }
]
"""

def test_return_loop_with_points_left():
    journey = Journey(returnLoop, listener)
    journey.selectPoints = lambda: "left"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("r01", "forward"),
        ("p01", "forward"),
        ("p01", "reverse"),
        ("outgoing points condition", "right"),
        ("s01", "reverse"),
        ("s01", "forward")
    ]

def test_return_loop_with_points_right():
    journey = Journey(returnLoop, listener)
    journey.selectPoints = lambda: "right"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("p01", "reverse"),
        ("r01", "reverse"),
        ("p01", "reverse"),
        ("outgoing points condition", "left"),
        ("s01", "reverse"),
        ("s01", "forward")
    ]

simpleFork = """
[
    {
        "id": "s01",
        "name": "main branch",
        "next": {
            "forward": {
                "id": "p01",
                "params": []
            }
        }
    },
    {
        "id": "s02",
        "name": "branch left",
        "next": {
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "left"]
            }
        }
    },
    {
        "id": "s03",
        "name": "branch right",
        "next": {
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "right"]
            }
        }
    },
    {
        "id": "p01",
        "type": "points",
        "name": "branching points",
        "outgoing": {
            "left": {
                "id": "s02"
            },
            "right": {
                "id": "s03"
            }
        }
    }
]
"""

def test_simple_fork_with_points_left():
    journey = Journey(simpleFork, listener)
    journey.selectPoints = lambda: "left"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "left"),
        ("s02", "forward"),
        ("s02", "reverse"),
        ("p01", "reverse"),
        ("outgoing points condition", "left"),
        ("s01", "reverse"),
        ("s01", "forward")
    ]

def test_simple_fork_with_points_right():
    journey = Journey(simpleFork, listener)
    journey.selectPoints = lambda: "right"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points selection", "right"),
        ("s03", "forward"),
        ("s03", "reverse"),
        ("p01", "reverse"),
        ("outgoing points condition", "right"),
        ("s01", "reverse"),
        ("s01", "forward")
    ]

simpleConvergingFork = """
[
    {
        "id": "s01",
        "name": "branch right",
        "next": {
            "forward": {
                "id": "p01",
                "params": ["outgoing", "right"]
            }
        }
    },
    {
        "id": "s02",
        "name": "branch left",
        "next": {
            "forward": {
                "id": "p01",
                "params": ["outgoing", "left"]
            }
        }
    },
    {
        "id": "s03",
        "name": "main branch",
        "next": {
            "reverse": {
                "id": "p01",
                "params": []
            }
        }
    },
    {
        "id": "p01",
        "type": "points",
        "name": "branching points",
        "outgoing": {
            "left": {
                "id": "s02"
            },
            "right": {
                "id": "s01"
            }
        }
    }
]
"""

def test_converging_fork_with_points_left():
    journey = Journey(simpleConvergingFork, listener)
    journey.selectPoints = lambda: "left"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("outgoing points condition", "right"),
        ("s03", "forward"),
        ("s03", "reverse"),
        ("p01", "reverse"),
        ("outgoing points selection", "left"),
        ("p01", "forward"),
        ("s02", "forward"),
        ("p01", "forward"),
        ("outgoing points condition", "left"),
        ("s03", "forward"),
        ("s03", "reverse")
    ]

triangleWithSidings = """
[
    {
        "id": "s01",
        "name": "siding one",
        "next": {
            "reverse": {
                "id": "p01",
                "params": []
            }
        }
    },
    {
        "id": "s02",
        "name": "curve 1-2",
        "next": {
            "forward": {
                "id": "p02",
                "params": ["outgoing", "right"]
            },
            "reverse": {
                "id": "p01",
                "params": ["outgoing", "left"]
            }
        }
    },
    {
        "id": "s03",
        "name": "siding two",
        "next": {
            "reverse": {
                "id": "p02",
                "params": []
            }
        }
    },
    {
        "id": "s04",
        "name": "curve 2-3",
        "next": {
            "forward": {
                "id": "p02",
                "params": ["outgoing", "left"]
            },
            "reverse": {
                "id": "p03",
                "params": ["outgoing", "right"]
            }
        }
    },
    {
        "id": "s05",
        "name": "siding three",
        "next": {
            "forward": {
                "id": "p03",
                "params": []
            }
        }
    },
    {
        "id": "s06",
        "name": "curve 3-1",
        "next": {
            "forward": {
                "id": "p01",
                "params": ["outgoing", "right"]
            },
            "reverse": {
                "id": "p03",
                "params": ["outgoing", "left"]
            }
        }
    },
    {
        "id": "p01",
        "type": "points",    
        "name": "apex one",
        "outgoing": {
            "left": {
                "id": "s02"
            },
            "right": {
                "id": "s06",
                "direction": "reverse"
            }
        }
    },
    {
        "id": "p02",
        "type": "points",
        "name": "apex two",
        "outgoing": {
            "left": {
                "id": "s04",
                "direction": "reverse"
            },
            "right": {
                "id": "s02",
                "direction": "reverse"
            }
        }
    },
    {
        "id": "p03",
        "type": "points",
        "name": "apex three",
        "outgoing": {
            "left": {
                "id": "s06"
            },
            "right": {
                "id": "s04"
            }
        }
    }
]
"""

def test_triangle_with_with_points_right():
    journey = Journey(triangleWithSidings, listener)
    journey.selectPoints = lambda: "right"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("outgoing points selection", "right"),
        ("s06", "reverse"),
        ("p03", "reverse"),
        ("outgoing points condition", "left"),
        ("s05", "reverse"),
        ("s05", "forward"),
        ("p03", "forward"),
        ("outgoing points selection", "right"),
        ("s04", "forward"),
        ("p02", "forward"),
        ("outgoing points condition", "left"),
        ("s03", "forward"),
        ("s03", "reverse"),
        ("p02", "reverse"),
        ("outgoing points selection", "right"),
        ("s02", "reverse"),
        ("p01", "reverse"),
        ("p01", "forward"),
        ("outgoing points condition", "left"),
        ("s01", "forward")
    ]

def test_triangle_with_with_points_left():
    journey = Journey(triangleWithSidings, listener)
    journey.selectPoints = lambda: "left"
    journey.start()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("outgoing points selection", "left"),
        ("p01", "forward"),
        ("s02", "forward"),
        ("p02", "forward"),
        ("outgoing points condition", "right"),
        ("s03", "forward"),
        ("s03", "reverse"),
        ("p02", "reverse"),
        ("outgoing points selection", "left"),
        ("s04", "reverse"),
        ("p03", "reverse"),
        ("outgoing points condition", "right"),
        ("s05", "reverse"),
        ("s05", "forward"),
        ("p03", "forward"),
        ("outgoing points selection", "left"),
        ("s06", "forward"),
        ("p01", "forward"),
        ("outgoing points condition", "right"),
        ("s01", "forward")
    ]
