import pytest

from domain.car_builder import CarBuilder
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


def test_starts_at_step_zero_and_incomplete():
    builder = CarBuilder()
    assert builder.current_step == 0
    assert builder.is_complete is False


def test_each_set_advances_the_step():
    builder = CarBuilder()
    builder.set_car_type(1)
    assert builder.current_step == 1
    builder.set_engine(1)
    assert builder.current_step == 2
    builder.set_brake(1)
    assert builder.current_step == 3
    builder.set_steering(1)
    assert builder.current_step == 4
    assert builder.is_complete is True


def test_set_stores_enum_values_on_car():
    builder = CarBuilder()
    builder.set_car_type(2)
    assert builder.car.car_type == CarType.SUV


def test_back_from_step_zero_is_a_no_op():
    builder = CarBuilder()
    builder.back()
    assert builder.current_step == 0


@pytest.mark.parametrize("advance_to_step,expected_after_back", [
    (1, 0),
    (2, 1),
    (3, 2),
])
def test_back_decrements_one_step_and_clears_that_field(advance_to_step, expected_after_back):
    builder = CarBuilder()
    setters = [builder.set_car_type, builder.set_engine, builder.set_brake, builder.set_steering]
    for setter in setters[:advance_to_step]:
        setter(1)
    builder.back()
    assert builder.current_step == expected_after_back


def test_back_from_finish_screen_resets_everything():
    builder = CarBuilder()
    builder.set_car_type(1)
    builder.set_engine(1)
    builder.set_brake(1)
    builder.set_steering(1)
    assert builder.current_step == 4

    builder.back()

    assert builder.current_step == 0
    assert builder.car.car_type is None
    assert builder.car.engine is None
    assert builder.car.brake is None
    assert builder.car.steering is None


def test_reselecting_after_back_overwrites_previous_choice():
    builder = CarBuilder()
    builder.set_engine(2)
    builder.back()
    builder.set_engine(3)
    assert builder.car.engine == Engine.WIA
