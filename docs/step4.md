# Step 4. CLI 분리 (`AssemblyStep` / `ConsoleView` / `AssemblyController`)

> Plan.md 3장 "단계별 진행 계획"의 4단계에 대한 상세 작업 명세.
> Step 1~3에서 도메인 레이어(`Car`, `CarBuilder`, `CompatibilityChecker`)를 완성했다. 이번
> 단계는 `assembly.py`에 남아있는 **입출력·화면 흐름 코드**를 별도 `cli/` 패키지로 옮겨
> `AssemblyStep`(Enum) + `ConsoleView`(출력) + `AssemblyController`(입력 루프/오케스트레이션)
> 세 조각으로 나눈다.
>
> `assembly.py`는 **이번 단계에서는 삭제하지 않는다.** 기존 스크립트는 그대로 동작 가능한
> 상태로 남겨두고, `cli/`+`main.py`라는 새 실행 경로를 나란히 만들어 충분히 검증한 뒤,
> `assembly.py`/`test_assembly.py` 정리와 진입점 교체는 Step 5에서 한 번에 처리한다
> (Step 1이 `domain/`을 `assembly.py` 옆에 병행 도입했던 것과 동일한 방식).

## 1. 목표

- **P5 해결**: `show_menu`, `is_valid_range`의 `step`(정수) 기준 if/elif 체인을 `AssemblyStep`
  Enum과 그에 딸린 데이터(메뉴 문구, 입력 유효범위) 테이블로 대체한다. 이제 새 단계를 추가하려면
  이 테이블에 항목 하나만 추가하면 된다.
- **P4 해결**: `input()`/`print()`/`time.sleep()` 같은 부작용을 `ConsoleView` 하나로 모으고,
  `AssemblyController`가 `CarBuilder`/`CompatibilityChecker`/`ConsoleView`를 조합해 기존
  `main()`의 역할을 수행하게 한다.
- 이 구조가 되면 **`input()`을 몬키패치하는 것만으로 전체 마법사 흐름을 엔드투엔드로 테스트**할 수
  있다 (P7에서 지적한 "테스트 불가능한 구조" 문제의 실질적 해결책).

## 2. 대상 파일 (신규 생성, `assembly.py`는 그대로 둠)

```
cli/
  __init__.py
  steps.py        # AssemblyStep(Enum), MENUS, INPUT_RANGES
  view.py         # ConsoleView
  controller.py   # AssemblyController
main.py           # 신규 진입점 (아직 "공식" 실행 스크립트는 아님 — Step 5에서 전환)
tests/
  cli/
    __init__.py
    test_steps.py
    test_view.py
    test_controller.py
```

## 3. 세부 작업

### 3.1 `cli/steps.py` — 단계 정의 + 메뉴/유효범위 테이블

```python
from enum import Enum


class AssemblyStep(Enum):
    CAR_TYPE = 0
    ENGINE = 1
    BRAKE = 2
    STEERING = 3
    FINISH = 4


MENUS = {
    AssemblyStep.CAR_TYPE: (
        "        ______________",
        "       /|            |",
        "  ____/_|_____________|____",
        " |                      O  |",
        " '-(@)----------------(@)--'",
        "===============================",
        "어떤 차량 타입을 선택할까요?",
        "1. Sedan",
        "2. SUV",
        "3. Truck",
    ),
    AssemblyStep.ENGINE: (
        "어떤 엔진을 탑재할까요?",
        "0. 뒤로가기",
        "1. GM",
        "2. TOYOTA",
        "3. WIA",
        "4. 고장난 엔진",
    ),
    AssemblyStep.BRAKE: (
        "어떤 제동장치를 선택할까요?",
        "0. 뒤로가기",
        "1. MANDO",
        "2. CONTINENTAL",
        "3. BOSCH",
    ),
    AssemblyStep.STEERING: (
        "어떤 조향장치를 선택할까요?",
        "0. 뒤로가기",
        "1. BOSCH",
        "2. MOBIS",
    ),
    AssemblyStep.FINISH: (
        "멋진 차량이 완성되었습니다.",
        "0. 처음 화면으로 돌아가기",
        "1. RUN",
        "2. Test",
    ),
}


# step 별 (최소값, 최대값, 에러 메시지)
INPUT_RANGES = {
    AssemblyStep.CAR_TYPE: (1, 3, "차량 타입은 1 ~ 3 범위만 선택 가능"),
    AssemblyStep.ENGINE: (0, 4, "엔진은 1 ~ 4 범위만 선택 가능"),
    AssemblyStep.BRAKE: (0, 3, "제동장치는 1 ~ 3 범위만 선택 가능"),
    AssemblyStep.STEERING: (0, 2, "조향장치는 1 ~ 2 범위만 선택 가능"),
    AssemblyStep.FINISH: (0, 2, "Run 또는 Test 중 하나를 선택 필요"),
}
```

- `CAR_TYPE`만 최소값이 `1`인 이유: 원본 코드에서도 최초 화면(step 0)에는 "뒤로가기"가 없었다
  (더 이전 단계가 없으므로). 이 비대칭성이 원본에 이미 있던 규칙이라 그대로 테이블에 반영했다.
- `CarBuilder.current_step`이 반환하는 값(0~4, `int`)은 `AssemblyStep(값)`으로 그대로
  변환 가능하도록 Enum 값을 원본 `step` 정수와 동일하게 맞췄다 — 이 값 일치가 Step 3
  (`CarBuilder`)과 Step 4를 이어주는 접점이다.

### 3.2 `cli/view.py` — 출력 전담, 도메인 지식 없음

```python
import sys
import time

from cli.steps import AssemblyStep, MENUS

CLEAR_SCREEN = "\033[H\033[2J"


class ConsoleView:
    def clear(self) -> None:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()

    def delay(self, ms: int) -> None:
        time.sleep(ms / 1000.0)

    def show_menu(self, step: AssemblyStep) -> None:
        self.clear()
        for line in MENUS[step]:
            print(line)
        print("===============================")

    def print_message(self, text: str) -> None:
        print(text)
```

`ConsoleView`는 `AssemblyStep`과 문자열만 알 뿐, `Car`/`CarType`/`Engine` 같은 도메인 타입은
전혀 참조하지 않는다 — 도메인이 바뀌어도 이 클래스는 수정할 필요가 없다.

### 3.3 `cli/controller.py` — 입력 루프 + 오케스트레이션

`select_*`, `run_produced_car`, `test_produced_car`가 하던 "도메인 갱신 + 결과를 문구로
표시"는 본질적으로 CLI 프레젠테이션 로직이므로, `assembly.py`에서 그대로 옮기지 않고
`AssemblyController`의 private 메서드로 재배치한다.

```python
from domain.car_builder import CarBuilder
from domain.compatibility import CompatibilityChecker
from domain.parts import Engine

from cli.steps import AssemblyStep, INPUT_RANGES
from cli.view import ConsoleView


class AssemblyController:
    def __init__(self, view: ConsoleView = None, checker: CompatibilityChecker = None):
        self._view = view or ConsoleView()
        self._checker = checker or CompatibilityChecker()
        self._builder = CarBuilder()

    def run(self) -> None:
        while True:
            step = AssemblyStep(self._builder.current_step)
            self._view.show_menu(step)
            buf = input("INPUT > ").strip()

            if buf == "exit":
                self._view.print_message("바이바이")
                break

            try:
                ans = int(buf)
            except ValueError:
                self._view.print_message("ERROR :: 숫자만 입력 가능")
                self._view.delay(800)
                continue

            if not self._is_valid_range(step, ans):
                self._view.delay(800)
                continue

            if ans == 0:
                self._builder.back()
                continue

            self._handle_step(step, ans)

    def _is_valid_range(self, step: AssemblyStep, ans: int) -> bool:
        min_value, max_value, error_message = INPUT_RANGES[step]
        if ans < min_value or ans > max_value:
            self._view.print_message(f"ERROR :: {error_message}")
            return False
        return True

    def _handle_step(self, step: AssemblyStep, ans: int) -> None:
        if step == AssemblyStep.CAR_TYPE:
            self._select_car_type(ans)
        elif step == AssemblyStep.ENGINE:
            self._select_engine(ans)
        elif step == AssemblyStep.BRAKE:
            self._select_brake(ans)
        elif step == AssemblyStep.STEERING:
            self._select_steering(ans)
        elif step == AssemblyStep.FINISH:
            self._handle_finish(ans)
            return
        self._view.delay(800)

    def _select_car_type(self, ans: int) -> None:
        self._builder.set_car_type(ans)
        self._view.print_message(f"차량 타입으로 {self._builder.car.car_type.label}을 선택하셨습니다.")

    def _select_engine(self, ans: int) -> None:
        self._builder.set_engine(ans)
        engine = self._builder.car.engine
        if engine == Engine.BROKEN:
            self._view.print_message("고장난 엔진을 선택하셨습니다.")
        else:
            self._view.print_message(f"{engine.label} 엔진을 선택하셨습니다.")

    def _select_brake(self, ans: int) -> None:
        self._builder.set_brake(ans)
        self._view.print_message(f"{self._builder.car.brake.label} 제동장치를 선택하셨습니다.")

    def _select_steering(self, ans: int) -> None:
        self._builder.set_steering(ans)
        self._view.print_message(f"{self._builder.car.steering.label} 조향장치를 선택하셨습니다.")

    def _handle_finish(self, ans: int) -> None:
        if ans == 1:
            self._run_produced_car()
            self._view.delay(2000)
        elif ans == 2:
            self._view.print_message("Test...")
            self._view.delay(1500)
            self._test_produced_car()
            self._view.delay(2000)

    def _run_produced_car(self) -> None:
        car = self._builder.car
        result = self._checker.check(car)
        if not result.passed:
            self._view.print_message("자동차가 동작되지 않습니다")
            return
        if car.engine == Engine.BROKEN:
            self._view.print_message("엔진이 고장나있습니다.")
            self._view.print_message("자동차가 움직이지 않습니다.")
            return

        self._view.print_message(f"Car Type : {car.car_type.label}")
        self._view.print_message(f"Engine   : {car.engine.label}")
        self._view.print_message(f"Brake    : {car.brake.label}")
        self._view.print_message(f"Steering : {car.steering.label}")
        self._view.print_message("자동차가 동작됩니다.")

    def _test_produced_car(self) -> None:
        result = self._checker.check(self._builder.car)
        if result.passed:
            self._view.print_message("PASS")
        else:
            self._view.print_message(f"FAIL\n{result.reason}")
```

- 생성자에서 `view`/`checker`를 주입받게 해, 테스트에서 `ConsoleView`를 대체하거나
  `CompatibilityChecker`에 가짜 규칙을 주입할 수 있게 했다 (Step 2에서 이미 이렇게 설계된
  `CompatibilityChecker(rules=...)`를 그대로 재사용).
- `_handle_step`에서 `FINISH`만 분기 끝에 `return`으로 빠지는 이유: 원본 `main()`도 `step==4`
  분기에서는 `RUN`/`Test` 처리 안에서 각자 다른 `delay`(2000ms, 1500+2000ms)를 직접 호출했고
  공통 `delay(800)`을 거치지 않았다. 이 비대칭도 원본 동작 그대로 보존한 것이다.
- `assembly.py`의 독립 함수였던 `is_valid_check(car)`는 이제 `_run_produced_car` 안에서
  `self._checker.check(car)`로 바로 호출한다 — 별도 boolean 래퍼가 없어도 되는 이유는,
  `run_produced_car`가 항상 실패 사유(`reason`)까지 함께 필요로 하지는 않지만 어차피
  `CompatibilityChecker.check()` 결과 하나로 `passed`만 보면 되기 때문. 동작은 동일.

### 3.4 `main.py` — 신규 진입점 (병행 상태, 아직 "공식"은 아님)

```python
from cli.controller import AssemblyController


def main():
    AssemblyController().run()


if __name__ == "__main__":
    main()
```

## 4. 테스트

### 4.1 `tests/cli/test_steps.py`

```python
from cli.steps import AssemblyStep, MENUS, INPUT_RANGES


def test_every_step_has_a_menu_and_input_range():
    for step in AssemblyStep:
        assert step in MENUS
        assert step in INPUT_RANGES


def test_car_type_step_does_not_allow_back():
    min_value, _, _ = INPUT_RANGES[AssemblyStep.CAR_TYPE]
    assert min_value == 1
```

### 4.2 `tests/cli/test_view.py`

```python
from cli.steps import AssemblyStep
from cli.view import ConsoleView


def test_show_menu_prints_menu_lines_and_separator(capsys):
    view = ConsoleView()
    view.show_menu(AssemblyStep.STEERING)
    out = capsys.readouterr().out
    assert "어떤 조향장치를 선택할까요?" in out
    assert out.strip().endswith("===============================")


def test_print_message_just_prints(capsys):
    ConsoleView().print_message("hello")
    assert capsys.readouterr().out.strip() == "hello"
```

### 4.3 `tests/cli/test_controller.py` — 엔드투엔드 (input 몬키패치)

이 구조 덕분에 이제 **마법사 전체 흐름**을 `input()`만 몬키패치해서 테스트할 수 있다.
`time.sleep`도 함께 몬키패치해 테스트 속도를 확보한다.

```python
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
    # 1(Sedan) -> 0(뒤로가기, engine 단계에서 car_type 재입력 화면으로) -> 2(SUV)로 정정 -> ... -> RUN
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


def test_exit_prints_goodbye(monkeypatch, capsys):
    _feed(monkeypatch, ["exit"])
    AssemblyController().run()
    assert "바이바이" in capsys.readouterr().out
```

## 5. 완료 조건 (Definition of Done)

- [ ] `cli/steps.py`, `cli/view.py`, `cli/controller.py`, `main.py` 생성
- [ ] `tests/cli/` 전체 통과 (`pytest tests/cli -v`)
- [ ] `python main.py`로 수동 실행 — 정상 플로우/뒤로가기/exit/잘못된 입력/RUN/Test 시나리오가
      `assembly.py`(Step 3 결과물)와 화면 출력이 완전히 동일한지 비교 확인
- [ ] `assembly.py`, `test_assembly.py`는 **수정하지 않고 그대로 둠** (Step 5에서 정리)

## 6. Non-goals (이 단계에서 하지 않는 것)

- `assembly.py` / `test_assembly.py` 삭제, `main.py`를 "공식" 진입점으로 문서/스크립트에서
  교체하는 작업 → Step 5
- `domain/` 레이어 자체의 추가 변경 없음 (Step 1~3 산출물을 그대로 소비만 함)
- 메뉴 문구·에러 메시지 문구 자체를 다듬는 것(문구 톤 통일 등) → 범위 밖. 이번 단계는 순수
  구조 재배치

## 7. 다음 단계와의 연결

Step 5는 이 단계에서 검증된 `cli/`+`domain/` 조합이 `assembly.py`와 동일하게 동작함을
최종 확인한 뒤, `assembly.py`/`test_assembly.py`를 삭제하고 `main.py`를 유일한 실행
진입점으로 확정하는 마무리 작업이 된다. 또한 `test_assembly.py`의 `assert False` 스텁들도
이 시점에 삭제 — 이미 `tests/domain/`, `tests/cli/`가 같은 대상을 실질적으로 커버하고 있기
때문에 별도 이관 없이 제거만 하면 된다.
