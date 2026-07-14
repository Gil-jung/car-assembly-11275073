import pytest

from domain.car import Car
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


def test_default_car_is_not_complete():
    car = Car()
    assert car.is_complete is False


def test_partially_filled_car_is_not_complete():
    car = Car(car_type=CarType.SEDAN, engine=Engine.GM)
    assert car.is_complete is False


def test_fully_filled_car_is_complete():
    car = Car(
        car_type=CarType.SEDAN,
        engine=Engine.GM,
        brake=BrakeSystem.MANDO,
        steering=SteeringSystem.BOSCH,
    )
    assert car.is_complete is True


def test_car_is_immutable():
    car = Car(car_type=CarType.SEDAN)
    with pytest.raises(AttributeError):
        car.car_type = CarType.SUV
