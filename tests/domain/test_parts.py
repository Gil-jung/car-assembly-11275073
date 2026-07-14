import pytest

from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


@pytest.mark.parametrize("member,expected", [
    (CarType.SEDAN, "Sedan"),
    (CarType.SUV, "SUV"),
    (CarType.TRUCK, "Truck"),
])
def test_car_type_label(member, expected):
    assert member.label == expected


@pytest.mark.parametrize("member,expected", [
    (Engine.GM, "GM"),
    (Engine.TOYOTA, "TOYOTA"),
    (Engine.WIA, "WIA"),
    (Engine.BROKEN, "고장난 엔진"),
])
def test_engine_label(member, expected):
    assert member.label == expected


@pytest.mark.parametrize("member,expected", [
    (BrakeSystem.MANDO, "Mando"),
    (BrakeSystem.CONTINENTAL, "Continental"),
    (BrakeSystem.BOSCH, "Bosch"),
])
def test_brake_label(member, expected):
    assert member.label == expected


@pytest.mark.parametrize("member,expected", [
    (SteeringSystem.BOSCH, "Bosch"),
    (SteeringSystem.MOBIS, "Mobis"),
])
def test_steering_label(member, expected):
    assert member.label == expected


def test_every_enum_member_has_a_label():
    for enum_cls in (CarType, Engine, BrakeSystem, SteeringSystem):
        for member in enum_cls:
            assert isinstance(member.label, str) and member.label
