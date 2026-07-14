import pytest

from domain.car import Car
from domain.compatibility import CompatibilityChecker
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


@pytest.fixture
def checker():
    return CompatibilityChecker()


def test_fully_valid_combination_passes(checker):
    car = Car(CarType.SEDAN, Engine.GM, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    result = checker.check(car)
    assert result.passed is True
    assert result.reason is None


@pytest.mark.parametrize("car,expected_reason", [
    (
        Car(CarType.SEDAN, Engine.GM, BrakeSystem.CONTINENTAL, SteeringSystem.BOSCH),
        "Sedan에는 Continental제동장치 사용 불가",
    ),
    (
        Car(CarType.SUV, Engine.TOYOTA, BrakeSystem.MANDO, SteeringSystem.BOSCH),
        "SUV에는 TOYOTA엔진 사용 불가",
    ),
    (
        Car(CarType.TRUCK, Engine.WIA, BrakeSystem.CONTINENTAL, SteeringSystem.BOSCH),
        "Truck에는 WIA엔진 사용 불가",
    ),
    (
        Car(CarType.TRUCK, Engine.GM, BrakeSystem.MANDO, SteeringSystem.BOSCH),
        "Truck에는 Mando제동장치 사용 불가",
    ),
    (
        Car(CarType.SEDAN, Engine.GM, BrakeSystem.BOSCH, SteeringSystem.MOBIS),
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
    ),
])
def test_each_rule_is_detected(checker, car, expected_reason):
    result = checker.check(car)
    assert result.passed is False
    assert result.reason == expected_reason


def test_first_violated_rule_wins_when_multiple_rules_broken(checker):
    car = Car(CarType.TRUCK, Engine.WIA, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    result = checker.check(car)
    assert result.reason == "Truck에는 WIA엔진 사용 불가"


@pytest.mark.parametrize("car", [
    Car(),
    Car(car_type=CarType.SEDAN),
])
def test_incomplete_car_never_violates_a_rule(checker, car):
    assert checker.check(car).passed is True
