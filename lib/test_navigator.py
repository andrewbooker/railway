
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
        "speed": "express",
        "length": 10.6,
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
        "speed": "crawl",
        "length": 1.5,
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
    assert journey.history == [("s01", "forward"), ("p01", "forward"), ("s01", "forward"), ("p01", "forward")]

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
        ("s02", "forward"),
        ("s02", "reverse"),
        ("p01", "reverse"),
        ("s01", "reverse"),
        ("p01", "reverse"),
        ("s01", "reverse")]
    
