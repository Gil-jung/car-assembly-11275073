from dataclasses import replace

from domain.car import Car
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem

_FIELDS = ("car_type", "engine", "brake", "steering")
_ENUM_BY_FIELD = {
    "car_type": CarType,
    "engine": Engine,
    "brake": BrakeSystem,
    "steering": SteeringSystem,
}


class CarBuilder:
    def __init__(self):
        self._car = Car()

    @property
    def car(self) -> Car:
        return self._car

    @property
    def current_step(self) -> int:
        for i, field in enumerate(_FIELDS):
            if getattr(self._car, field) is None:
                return i
        return len(_FIELDS)

    @property
    def is_complete(self) -> bool:
        return self._car.is_complete

    def set_car_type(self, value: int) -> None:
        self._set("car_type", value)

    def set_engine(self, value: int) -> None:
        self._set("engine", value)

    def set_brake(self, value: int) -> None:
        self._set("brake", value)

    def set_steering(self, value: int) -> None:
        self._set("steering", value)

    def back(self) -> None:
        step = self.current_step
        if step == 0:
            return
        if step == len(_FIELDS):
            self._car = Car()
            return
        field_to_reconsider = _FIELDS[step - 1]
        self._car = replace(self._car, **{field_to_reconsider: None})

    def _set(self, field: str, value: int) -> None:
        enum_cls = _ENUM_BY_FIELD[field]
        self._car = replace(self._car, **{field: enum_cls(value)})
