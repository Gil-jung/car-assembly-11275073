import assembly
from domain.car import Car
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


def _car(car_type, engine, brake, steering):
    return Car(car_type, engine, brake, steering)


def test_is_valid_check_true_for_valid_combo():
    car = _car(CarType.SEDAN, Engine.GM, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    assert assembly.is_valid_check(car) is True


def test_is_valid_check_false_for_sedan_continental():
    car = _car(CarType.SEDAN, Engine.GM, BrakeSystem.CONTINENTAL, SteeringSystem.BOSCH)
    assert assembly.is_valid_check(car) is False


def test_test_produced_car_prints_pass(capsys):
    car = _car(CarType.SEDAN, Engine.GM, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    assembly.test_produced_car(car)
    assert capsys.readouterr().out.strip() == "PASS"


def test_test_produced_car_prints_fail_reason(capsys):
    car = _car(CarType.TRUCK, Engine.GM, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    assembly.test_produced_car(car)
    out = capsys.readouterr().out.strip()
    assert out == "FAIL\nTruck에는 Mando제동장치 사용 불가"


def test_run_produced_car_prints_summary(capsys):
    car = _car(CarType.SEDAN, Engine.GM, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    assembly.run_produced_car(car)
    out = capsys.readouterr().out
    assert "Car Type : Sedan" in out
    assert "Engine   : GM" in out
    assert "Brake    : Mando" in out
    assert "Steering : Bosch" in out
    assert "자동차가 동작됩니다." in out


def test_run_produced_car_with_broken_engine(capsys):
    car = _car(CarType.SEDAN, Engine.BROKEN, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    assembly.run_produced_car(car)
    out = capsys.readouterr().out
    assert "엔진이 고장나있습니다." in out
    assert "자동차가 움직이지 않습니다." in out
