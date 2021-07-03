
from navigator import Journey

def test_straight_line_track_at_start():
    journey = Journey("{\"sections\":[{\"id\":\"s1\",\"name\":\"shuttle\",\"next\":{}}]}")
    assert journey.history == [("s1", "forward")]
    
def test_straight_line_track_after_one_move():
    journey = Journey("{\"sections\":[{\"id\":\"s1\",\"name\":\"shuttle\",\"next\":{}}]}")
    journey.nextStage()
    assert journey.history == [("s1", "forward"),("s1", "reverse")]
    
def test_straight_line_track_after_multiple_moves():
    journey = Journey("{\"sections\":[{\"id\":\"s1\",\"name\":\"shuttle\",\"next\":{}}]}")
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    journey.nextStage()
    assert journey.history == [("s1", "forward"),("s1", "reverse"),("s1", "forward"),("s1", "reverse"),("s1", "forward")]
