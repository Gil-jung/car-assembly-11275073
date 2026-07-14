import pytest

from cli.controller import AssemblyController


@pytest.fixture(autouse=True)
def _no_delay(monkeypatch):
    monkeypatch.setattr("cli.view.time.sleep", lambda seconds: None)


def _feed(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


def test_happy_path_run(monkeypatch, capsys):
    _feed(monkeypatch, ["1", "1", "1", "1", "1", "exit"])  # Sedan/GM/Mando/Bosch -> RUN
    AssemblyController().run()
    out = capsys.readouterr().out
    assert "Car Type : Sedan" in out
    assert "자동차가 동작됩니다." in out


def test_happy_path_test_pass(monkeypatch, capsys):
    _feed(monkeypatch, ["1", "1", "1", "1", "2", "exit"])
    AssemblyController().run()
    assert "PASS" in capsys.readouterr().out


def test_incompatible_combo_reports_fail(monkeypatch, capsys):
    _feed(monkeypatch, ["1", "1", "2", "1", "2", "exit"])  # Sedan + Continental
    AssemblyController().run()
    out = capsys.readouterr().out
    assert "FAIL" in out
    assert "Sedan에는 Continental제동장치 사용 불가" in out


def test_back_navigation_returns_to_previous_step(monkeypatch, capsys):
    _feed(monkeypatch, ["1", "0", "2", "1", "1", "1", "1", "exit"])
    AssemblyController().run()
    out = capsys.readouterr().out
    assert "Car Type : SUV" in out


def test_invalid_number_shows_error_and_reprompts(monkeypatch, capsys):
    _feed(monkeypatch, ["9", "1", "1", "1", "1", "1", "exit"])
    AssemblyController().run()
    out = capsys.readouterr().out
    assert "ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능" in out


def test_non_numeric_input_shows_error(monkeypatch, capsys):
    _feed(monkeypatch, ["abc", "1", "1", "1", "1", "1", "exit"])
    AssemblyController().run()
    assert "ERROR :: 숫자만 입력 가능" in capsys.readouterr().out


def test_broken_engine_does_not_run(monkeypatch, capsys):
    _feed(monkeypatch, ["1", "4", "1", "1", "1", "exit"])
    AssemblyController().run()
    out = capsys.readouterr().out
    assert "엔진이 고장나있습니다." in out
    assert "자동차가 움직이지 않습니다." in out


def test_exit_prints_goodbye(monkeypatch, capsys):
    _feed(monkeypatch, ["exit"])
    AssemblyController().run()
    assert "바이바이" in capsys.readouterr().out
