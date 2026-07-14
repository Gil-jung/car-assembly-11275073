import assembly


def _set_globals(car_type, engine, brake, steering):
    assembly.q0 = car_type
    assembly.q1 = engine
    assembly.q2 = brake
    assembly.q3 = steering


def test_is_valid_check_true_for_valid_combo():
    _set_globals(1, 1, 1, 1)  # Sedan, GM, Mando, Bosch
    assert assembly.is_valid_check() is True


def test_is_valid_check_false_for_sedan_continental():
    _set_globals(1, 1, 2, 1)  # Sedan + Continental
    assert assembly.is_valid_check() is False


def test_test_produced_car_prints_pass(capsys):
    _set_globals(1, 1, 1, 1)
    assembly.test_produced_car()
    assert capsys.readouterr().out.strip() == "PASS"


def test_test_produced_car_prints_fail_reason(capsys):
    _set_globals(3, 1, 1, 1)  # Truck + Mando
    assembly.test_produced_car()
    out = capsys.readouterr().out.strip()
    assert out == "FAIL\nTruck에는 Mando제동장치 사용 불가"
