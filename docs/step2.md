# Step 2. 호환성 규칙 통합 (CompatibilityRule / CompatibilityChecker)

> Plan.md 3장 "단계별 진행 계획"의 2단계에 대한 상세 작업 명세.
> Step 1에서 만든 `Car`, `CarType`, `Engine`, `BrakeSystem`, `SteeringSystem`을 사용해
> **P3 (호환성 규칙 중복)** 를 해결한다. 이번 단계에서는 `assembly.py`의 `is_valid_check()`와
> `test_produced_car()` 내부 구현만 새 체커를 호출하도록 바꾸고, 전역 변수 `q0~q3`/`step`
> 자체는 아직 남겨둔다 (제거는 Step 3).

## 1. 목표

현재 동일한 호환성 규칙 5가지가 `is_valid_check()`(bool만 반환)와 `test_produced_car()`
(FAIL 메시지까지 반환) 두 곳에 따로 구현되어 있다. 규칙이 바뀔 때 한쪽만 고치면 `RUN`과
`Test` 메뉴의 결과가 서로 어긋나는 버그가 생길 수 있다. 이를 **단일 진실 공급원(SSOT)** 인
`CompatibilityChecker` 하나로 통합한다.

## 2. 대상 파일

```
domain/
  compatibility.py        # (신규) CompatibilityRule, CompatibilityChecker, CheckResult
tests/
  domain/
    test_compatibility.py # (신규)
assembly.py                # (수정) is_valid_check(), test_produced_car() 내부만 교체
tests/
  test_assembly_characterization.py  # (신규) 교체 전후 출력이 동일한지 캡처 검증
```

## 3. 세부 작업

### 3.1 기존 규칙 5가지 정리

| # | 조건 (기존 `q0~q3`) | 위반 시 메시지 |
|---|---|---|
| R1 | `car_type == SEDAN` and `brake == CONTINENTAL` | `Sedan에는 Continental제동장치 사용 불가` |
| R2 | `car_type == SUV` and `engine == TOYOTA` | `SUV에는 TOYOTA엔진 사용 불가` |
| R3 | `car_type == TRUCK` and `engine == WIA` | `Truck에는 WIA엔진 사용 불가` |
| R4 | `car_type == TRUCK` and `brake == MANDO` | `Truck에는 Mando제동장치 사용 불가` |
| R5 | `brake == BOSCH` and `steering != BOSCH` | `Bosch제동장치에는 Bosch조향장치 이외 사용 불가` |

기존 `test_produced_car()`는 `elif` 체인이라 **첫 번째로 위반된 규칙 하나만** 보고한다
(여러 규칙을 동시에 위반해도 첫 메시지만 출력). 이 "첫 위반 하나만 보고" 동작을 이번 단계에서도
**그대로 유지**한다 (동작 변경은 리팩토링 범위 밖 — Non-goals 참고).

> 참고: "엔진이 고장남"(`Engine.BROKEN`)은 부품 간 호환성 문제가 아니라 개별 부품 자체의 고장이므로
> `CompatibilityChecker`의 규칙 대상에 넣지 않는다. 기존처럼 `run_produced_car`에서 별도로 처리한다
> (아래 3.3 참고). 두 개념(설계 호환성 vs 개별 부품 고장)을 섞지 않는 것이 이번 통합의 전제.

### 3.2 `domain/compatibility.py`

```python
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


RULES: tuple[CompatibilityRule, ...] = (
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
    def __init__(self, rules: tuple[CompatibilityRule, ...] = RULES):
        self._rules = rules

    def check(self, car: Car) -> CheckResult:
        for rule in self._rules:
            if rule.is_violated(car):
                return CheckResult(passed=False, reason=rule.reason)
        return CheckResult(passed=True)
```

- 규칙 순서를 기존 `elif` 체인과 동일하게 유지해 "첫 위반 규칙 보고" 동작을 그대로 재현한다.
- `rules`를 생성자 인자로 받게 해 테스트에서 임의의 규칙 조합을 주입해 검증할 수 있게 한다
  (실 서비스 코드는 기본값 `RULES`를 그대로 사용).
- `Car`의 필드가 `None`인 경우(아직 다 선택되지 않은 상태) 모든 `==` 비교가 자연히 `False`가 되어
  위반으로 판정되지 않는다 — 즉 미완성 `Car`는 항상 `passed=True`로 나온다. 이 체커는
  "완성된 차량인지"는 판단하지 않고 "규칙을 위반했는지"만 판단한다 (완성 여부 확인은 호출자 책임,
  Step 3의 `CarBuilder.is_complete` 담당 영역).

### 3.3 `assembly.py` 변경 — 중복 제거만, 최소 침습

`q0~q3`(전역 int)는 이번 단계에서 그대로 둔다. `is_valid_check()`와 `test_produced_car()`
내부에서만 전역값을 `Car`로 변환해 `CompatibilityChecker`에 위임하도록 바꾼다.

```python
from domain.car import Car
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem
from domain.compatibility import CompatibilityChecker

_checker = CompatibilityChecker()


def _car_from_globals() -> Car:
    return Car(
        car_type=CarType(q0) if q0 else None,
        engine=Engine(q1) if q1 else None,
        brake=BrakeSystem(q2) if q2 else None,
        steering=SteeringSystem(q3) if q3 else None,
    )


def is_valid_check():
    return _checker.check(_car_from_globals()).passed


def test_produced_car():
    result = _checker.check(_car_from_globals())
    if result.passed:
        print("PASS")
    else:
        print(f"FAIL\n{result.reason}")
```

- `Engine(q1)`에서 `q1 == 4`(고장난 엔진)는 `Engine.BROKEN`으로 정상 매핑되지만, 위 규칙 어디에도
  `Engine.BROKEN`을 다루는 규칙이 없으므로 `is_valid_check()`는 항상 `True`를 반환한다.
  이는 **기존 동작과 동일**하다 — 기존 `is_valid_check()`도 고장난 엔진을 걸러내지 않았고,
  `run_produced_car()`가 `if q1 == 4: ...` 로 별도 처리했다. 이 별도 처리 코드는 이번 단계에서
  **건드리지 않는다**.
- `run_produced_car()` 자체의 부품 출력 로직(if/elif 문자열)은 이번 단계 범위 밖 (Step 1의
  `label` 프로퍼티로 대체하는 작업은 Step 3~4에서 `CarBuilder`/`ConsoleView` 도입과 함께 처리).

## 4. 테스트

### 4.1 `tests/domain/test_compatibility.py` — 규칙 자체 검증

```python
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
    # Truck + WIA엔진(R3) + Mando제동장치(R4) 동시 위반 -> 먼저 정의된 R3가 보고되어야 함
    # (기존 elif 체인의 "첫 위반만 보고" 동작 재현)
    car = Car(CarType.TRUCK, Engine.WIA, BrakeSystem.MANDO, SteeringSystem.BOSCH)
    result = checker.check(car)
    assert result.reason == "Truck에는 WIA엔진 사용 불가"


@pytest.mark.parametrize("car", [
    Car(),  # 아무것도 선택 안 됨
    Car(car_type=CarType.SEDAN),  # 일부만 선택됨
])
def test_incomplete_car_never_violates_a_rule(checker, car):
    assert checker.check(car).passed is True
```

### 4.2 `tests/test_assembly_characterization.py` — 회귀 방지(특성화 테스트)

`assembly.py`의 `is_valid_check`/`test_produced_car`가 **교체 전과 동일하게 동작**하는지
전역 변수를 직접 세팅해 검증한다 (Step 3에서 전역 변수가 사라지면 이 테스트는 자연스럽게 삭제/대체됨).

```python
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
```

## 5. 완료 조건 (Definition of Done)

- [ ] `domain/compatibility.py` 생성, `tests/domain/test_compatibility.py` 전부 통과
- [ ] `assembly.py`의 `is_valid_check()`, `test_produced_car()`가 `CompatibilityChecker`를
      호출하도록 교체되고, 기존 5가지 규칙의 if/elif 블록은 **삭제**됨
- [ ] `tests/test_assembly_characterization.py` 통과 — 교체 전/후 콘솔 출력이 완전히 동일함을 확인
- [ ] `run_produced_car()`의 "엔진 고장" 별도 처리(`if q1 == 4`)는 변경 없음
- [ ] 실제 CLI(`python assembly.py`)를 몇 가지 시나리오로 수동 실행해 RUN/Test 결과가 이전과 같은지 확인

## 6. Non-goals (이 단계에서 하지 않는 것)

- 전역 변수 `q0~q3`, `step` 제거 → Step 3 (`CarBuilder`)
- `test_produced_car()`가 위반된 규칙을 전부 보고하도록 동작을 바꾸는 것(현재는 첫 개만 보고) →
  범위 밖. 필요하다면 별도 개선 항목으로 제안만 하고 이번 리팩토링에서는 동작 유지
- "엔진 고장"을 `CompatibilityRule`로 편입하는 것 → 개념이 다르므로(호환성 vs 고장) 보류,
  필요 시 Step 3 이후 `CarBuilder`/`Car`에 별도 `is_operational` 같은 개념으로 분리 제안 가능
- `run_produced_car()`의 출력 문자열(부품 라벨 if/elif) 정리 → Step 3~4

## 7. 다음 단계와의 연결

Step 3(`CarBuilder`)는 전역 `q0~q3`를 없애고 `Car`를 직접 들고 다니게 되므로, 이 단계에서
만든 `_car_from_globals()`는 Step 3에서 자연스럽게 사라지고 `CarBuilder.build() -> Car`로
대체된다. `CompatibilityChecker`는 그대로 재사용된다 (변경 없음) — 이것이 이번 통합의 핵심 이점.
