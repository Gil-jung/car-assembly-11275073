from dataclasses import dataclass
from typing import Callable, Optional

from domain.car import Car
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


@dataclass(frozen=True)
class CompatibilityRule:
    reason: str
    is_violated: Callable[[Car], bool]


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    reason: Optional[str] = None


RULES = (
    CompatibilityRule(
        "Sedan에는 Continental제동장치 사용 불가",
        lambda car: car.car_type == CarType.SEDAN and car.brake == BrakeSystem.CONTINENTAL,
    ),
    CompatibilityRule(
        "SUV에는 TOYOTA엔진 사용 불가",
        lambda car: car.car_type == CarType.SUV and car.engine == Engine.TOYOTA,
    ),
    CompatibilityRule(
        "Truck에는 WIA엔진 사용 불가",
        lambda car: car.car_type == CarType.TRUCK and car.engine == Engine.WIA,
    ),
    CompatibilityRule(
        "Truck에는 Mando제동장치 사용 불가",
        lambda car: car.car_type == CarType.TRUCK and car.brake == BrakeSystem.MANDO,
    ),
    CompatibilityRule(
        "Bosch제동장치에는 Bosch조향장치 이외 사용 불가",
        lambda car: car.brake == BrakeSystem.BOSCH and car.steering != SteeringSystem.BOSCH,
    ),
)


class CompatibilityChecker:
    def __init__(self, rules=RULES):
        self._rules = rules

    def check(self, car: Car) -> CheckResult:
        for rule in self._rules:
            if rule.is_violated(car):
                return CheckResult(passed=False, reason=rule.reason)
        return CheckResult(passed=True)
