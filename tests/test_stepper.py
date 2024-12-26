import pytest
from ..src import stepper

@pytest.fixture
def ten_step_stepper():
    return stepper.stepper(num_steps=10)

def test_stepper_init(ten_step_stepper):
    assert ten_step_stepper.current_step == 0
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 9
    assert ten_step_stepper.stepping_forward
    assert ten_step_stepper.num_steps == 10

def test_stepper_advance_forward(ten_step_stepper):
    for value in [1,2,3,4,5,6,7,8,9,0,1,2,3]:
        assert ten_step_stepper.advance_step() == value

def test_stepper_advance_backward(ten_step_stepper):
    ten_step_stepper.reverse()
    assert not ten_step_stepper.stepping_forward
    for value in [9,8,7,6,5,4,3,2,1,0,9,8,7]:
        assert ten_step_stepper.advance_step() == value

def test_stepper_reset(ten_step_stepper):
    ten_step_stepper.current_step = 5
    ten_step_stepper.reset()
    assert ten_step_stepper.current_step == 0

def test_stepper_adjust_range_start(ten_step_stepper):
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 9
    ten_step_stepper.adjust_range_start(4) # no-op
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 9
    ten_step_stepper.adjust_range_start(-4) # no-op
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 9
    ten_step_stepper.first_step = 3
    ten_step_stepper.adjust_range_start(-2)
    assert ten_step_stepper.first_step == 1
    assert ten_step_stepper.last_step == 7
    ten_step_stepper.adjust_range_start(1)
    assert ten_step_stepper.first_step == 2
    assert ten_step_stepper.last_step == 8
    ten_step_stepper.adjust_range_start(8) # too far +
    assert ten_step_stepper.first_step == 3
    assert ten_step_stepper.last_step == 9
    ten_step_stepper.adjust_range_start(-8) # too far -
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 6

def test_stepper_adjust_range_length(ten_step_stepper):
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 9
    ten_step_stepper.adjust_range_length(4) # no-op
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 9
    ten_step_stepper.adjust_range_length(-4)
    assert ten_step_stepper.first_step == 0
    assert ten_step_stepper.last_step == 5
    ten_step_stepper.first_step = 3
    ten_step_stepper.adjust_range_length(-4) # too far -
    assert ten_step_stepper.first_step == 3
    assert ten_step_stepper.last_step == 3
    ten_step_stepper.adjust_range_length(4)
    assert ten_step_stepper.first_step == 3
    assert ten_step_stepper.last_step == 7
    ten_step_stepper.adjust_range_length(4) # too far +
    assert ten_step_stepper.first_step == 3
    assert ten_step_stepper.last_step == 9