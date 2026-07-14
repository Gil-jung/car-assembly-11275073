from enum import Enum


class CarType(Enum):
    SEDAN = 1
    SUV = 2
    TRUCK = 3

    @property
    def label(self) -> str:
        return {
            CarType.SEDAN: "Sedan",
            CarType.SUV: "SUV",
            CarType.TRUCK: "Truck",
        }[self]


class Engine(Enum):
    GM = 1
    TOYOTA = 2
    WIA = 3
    BROKEN = 4

    @property
    def label(self) -> str:
        return {
            Engine.GM: "GM",
            Engine.TOYOTA: "TOYOTA",
            Engine.WIA: "WIA",
            Engine.BROKEN: "고장난 엔진",
        }[self]


class BrakeSystem(Enum):
    MANDO = 1
    CONTINENTAL = 2
    BOSCH = 3

    @property
    def label(self) -> str:
        return {
            BrakeSystem.MANDO: "Mando",
            BrakeSystem.CONTINENTAL: "Continental",
            BrakeSystem.BOSCH: "Bosch",
        }[self]


class SteeringSystem(Enum):
    BOSCH = 1
    MOBIS = 2

    @property
    def label(self) -> str:
        return {
            SteeringSystem.BOSCH: "Bosch",
            SteeringSystem.MOBIS: "Mobis",
        }[self]
