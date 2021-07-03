
from navigator import Journey

straightLine = "{\"sections\":[{\"id\":\"s1\",\"name\":\"shuttle\",\"next\":{}}]}"

def test_straight_line_track_at_start():
    journey = Journey(straightLine)
    assert journey.history == [("s1", "forward")]

def test_straight_line_track_after_one_move():
    journey = Journey(straightLine)
    journey.nextStage()
    assert journey.history == [("s1", "forward"),("s1", "reverse")]

def test_straight_line_track_after_multiple_moves():
    journey = Journey(straightLine)
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s1", "forward"),("s1", "reverse"),("s1", "forward"),("s1", "reverse"),("s1", "forward")]


loop = "{\"sections\":[{\"id\":\"s01\",\"name\":\"loop\",\"next\":{\"forward\":{\"id\":\"s01\"},\"reverse\":{\"id\":\"s01\"}}}]}"

def test_loop_at_start():
    journey = Journey(loop)
    assert journey.history == [("s01", "forward")]

def test_loop_after_multiple_moves():
    journey = Journey(loop)
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s01", "forward"),("s01", "forward"),("s01", "forward")]

def test_loop_after_change_of_direction():
    journey = Journey(loop)
    journey.nextStage()
    journey.changeDirection()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s01", "forward"),("s01", "forward"),("s01", "reverse"),("s01", "reverse"),("s01", "reverse")]


loopWithSiding = """
{"sections":[
    {
        "id": "s01",
        "name": "main loop",
        "next": {
            "forward": {
                "id": "p01"
            },
            "reverse": {
                "id": "p01",
                "param": "right"
            }
        }
    },
    {
        "id": "s02",
        "name": "branch siding",
        "next": {
            "reverse": {
                "id": "p01",
                "param": "left"
            }
        }
    }
],
"points": [
    {
        "id": "p01",
        "name": "branch siding points",
        "left": {
            "id": "s02"
        },
        "right": {
            "id": "s01"
        }
    }
]}
"""

def test_loop_with_siding_points_right():
    journey = Journey(loopWithSiding)
    journey.selectPoints = lambda: "right"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("points selection", "right"),
        ("s01", "forward"),
        ("p01", "forward")]
        
def test_loop_with_siding_points_right_in_reverse():
    journey = Journey(loopWithSiding)
    journey.selectPoints = lambda: "right"
    journey.nextStage()
    journey.direction = "reverse"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("points condition", "right"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("points condition", "right"),
        ("s01", "reverse")]

def test_loop_with_siding_points_left():
    journey = Journey(loopWithSiding)
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
        ("points selection", "left"),
        ("s02", "forward"),
        ("s02", "reverse"),
        ("p01", "reverse"),
        ("points condition", "left"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("points condition", "right"),
        ("s01", "reverse")]
    
returnLoop = """
{
    "sections": [
        {
            "id": "s01",
            "name": "main branch",
            "next": {
                "forward": {
                    "id": "p01"
                }
            }
        },
        {
            "id": "r01",
            "name": "return loop",
            "next": {
                "forward": {
                    "id": "p01",
                    "param": "right"
                },
                "reverse": {
                    "id": "p01",
                    "param": "left"
                }
            }
        }
    ],
    "points": [
        {
            "id": "p01",
            "name": "return loop points",
            "left": {
                "id": "r01"
            },
            "right": {
                "id": "r01",
                "direction": "reverse"
            }
        }
    ]
}
"""

def test_return_loop_with_points_left():
    journey = Journey(returnLoop)
    journey.selectPoints = lambda: "left"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("points selection", "left"),
        ("r01", "forward"),
        ("p01", "forward"),
        ("p01", "reverse"),
        ("points condition", "right"),
        ("s01", "reverse"),
        ("s01", "forward")
    ]

def test_return_loop_with_points_right():
    journey = Journey(returnLoop)
    journey.selectPoints = lambda: "right"
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [
        ("s01", "forward"),
        ("p01", "forward"),
        ("points selection", "right"),
        ("p01", "reverse"),
        ("r01", "reverse"),
        ("p01", "reverse"),
        ("points condition", "left"),
        ("s01", "reverse"),
        ("s01", "forward")
    ]
