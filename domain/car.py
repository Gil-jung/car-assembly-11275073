from dataclasses import dataclass
from typing import Optional

from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


@dataclass(frozen=True)
class Car:
    car_type: Optional[CarType] = None
    engine: Optional[Engine] = None
    brake: Optional[BrakeSystem] = None
    steering: Optional[SteeringSystem] = None

    @property
    def is_complete(self) -> bool:
        return None not in (self.car_type, self.engine, self.brake, self.steering)
