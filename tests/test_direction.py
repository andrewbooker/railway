from lib.directionController import Direction


def test_can_find_direction_from_string():
    assert Direction.value_of("forward") == Direction.Forward
    assert Direction.value_of("reverse") == Direction.Reverse
    assert Direction.value_of("") == Direction.Forward


def test_can_find_opposite():
    assert Direction.Forward.opposite() == Direction.Reverse
    assert Direction.Reverse.opposite() == Direction.Forward