# Step 3. CarBuilder 도입 (전역 상태 `q0~q3` / `step` 제거)

> Plan.md 3장 "단계별 진행 계획"의 3단계에 대한 상세 작업 명세.
> Step 2까지는 `q0~q3`(전역 변수)를 그대로 두고 `_car_from_globals()`로 우회했다.
> 이번 단계에서 그 우회를 걷어내고, **선택 상태 자체를 `CarBuilder` 객체 하나가 소유**하도록 바꾼다.
> `main()`의 while 루프 구조와 화면 문구(`show_menu`, 확인 메시지 등)는 최대한 그대로 유지하고,
> `input()`/`print()` 를 별도 클래스로 쪼개는 작업(`ConsoleView`/`AssemblyController`)은 Step 4로 미룬다.

## 1. 목표

- **P1 해결**: 모듈 전역 변수 `q0, q1, q2, q3`를 제거하고, 조립 중인 차량 상태를 `CarBuilder`
  인스턴스 하나가 들고 다니게 한다. 이제 이론상 조립 프로세스 두 개를 동시에 띄워도 서로 상태가
  섞이지 않는다 (지금 당장 필요하진 않지만, 전역 상태가 없다는 것 자체가 테스트 격리·확장성의
  전제 조건이다).
- **"현재 단계(step)" 계산을 CarBuilder가 전담**하게 하여, `main()`이 별도로 `step` 변수를
  증가시키거나 "뒤로가기 시 몇 단계 되돌아갈지"를 계산하지 않아도 되게 한다. → step 진행/후퇴 로직이
  한 곳(`CarBuilder`)에만 존재.
- Step 2에서 남겨뒀던 **완전히 죽은 코드**(dead code)를 함께 정리한다: `CarType_Q`, `Engine_Q`,
  `brakeSystem_Q`, `SteeringSystem_Q`, `Run_Test`, `q4`, 그리고 Step 2 이후로 더 이상
  아무 곳에서도 참조되지 않는 `SEDAN/SUV/TRUCK/GM/TOYOTA/WIA/MANDO/CONTINENTAL/BOSCH_B/BOSCH_S/MOBIS`
  상수 전체.

## 2. 대상 파일

```
domain/
  car_builder.py            # (신규) CarBuilder
tests/
  domain/
    test_car_builder.py     # (신규)
assembly.py                  # (수정) 전역 q0~q3 제거, CarBuilder로 상태 이전
tests/
  test_assembly_characterization.py  # (수정) 전역 변수 대신 Car/CarBuilder 기반으로 갱신
```

## 3. 세부 작업

### 3.1 `domain/car_builder.py`

`Car`는 Step 1에서 `frozen=True`로 만들었으므로, 필드를 하나씩 채우는 과정은 매번 새
`Car`를 만들어 교체하는 방식(`dataclasses.replace`)으로 구현한다.

```python
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
        """아직 채워지지 않은 첫 필드의 인덱스(0~3). 4면 모든 부품이 채워진 '완성' 단계."""
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
            # 완성 화면("처음 화면으로 돌아가기")에서는 전체를 초기화하고 처음부터 다시 시작한다.
            self._car = Car()
            return
        field_to_reconsider = _FIELDS[step - 1]
        self._car = replace(self._car, **{field_to_reconsider: None})

    def _set(self, field: str, value: int) -> None:
        enum_cls = _ENUM_BY_FIELD[field]
        self._car = replace(self._car, **{field: enum_cls(value)})
```

#### `back()` 동작이 기존 `main()`과 동일함을 확인

| 현재 `current_step` | 기존 `main()`의 `ans==0` 처리 | `CarBuilder.back()` 처리 | 결과 |
|---|---|---|---|
| 0 (차량 타입 선택 화면) | `step > 0`이 거짓 → 아무 것도 안 함 | `step==0`이면 즉시 return | 동일 |
| 1 (엔진 선택 화면) | `step = step - 1` → 0 | `car_type`을 지움 → `current_step`이 0으로 재계산 | 동일 |
| 2 (제동장치 선택 화면) | `step = step - 1` → 1 | `engine`을 지움 → `current_step`이 1로 재계산 | 동일 |
| 3 (조향장치 선택 화면) | `step = step - 1` → 2 | `brake`를 지움 → `current_step`이 2로 재계산 | 동일 |
| 4 (완성 화면) | `step = 0` (그 사이 값 무시, 바로 0으로 점프) | 전체 `Car()`로 초기화 → `current_step`이 0 | 동일 |

> 4번 케이스는 원래 코드도 `q0~q3` 값을 지우지 않고 `step`만 0으로 되돌렸다(부품 값은 그대로
> 남아있는 상태였음). 하지만 화면 흐름상 `step=0`에서 다시 진행하면 4개 부품을 무조건 다시
> 순서대로 선택해야 하므로(건너뛰고 완성 화면으로 갈 방법이 없음), 남아있던 값이 실제로
> 화면에 노출되거나 최종 결과에 영향을 준 적은 없다. 따라서 `CarBuilder.back()`이 이 시점에
> 아예 `Car()`로 초기화하는 것은 **관찰 가능한 동작 변화 없이** 내부 상태를 더 일관되게 만드는
> 개선이다.

### 3.2 `assembly.py` 변경

#### (a) 죽은 코드 제거

```python
# 삭제 대상 (Step 2 이후 어디서도 참조되지 않음)
CarType_Q = 0
Engine_Q = 1
brakeSystem_Q = 2
SteeringSystem_Q = 3
Run_Test = 4

SEDAN = 1
SUV = 2
TRUCK = 3
GM = 1
TOYOTA = 2
WIA = 3
MANDO = 1
CONTINENTAL = 2
BOSCH_B = 3
BOSCH_S = 1
MOBIS = 2

q0 = 0
q1 = 0
q2 = 0
q3 = 0
q4 = 0

_checker = CompatibilityChecker()

def _car_from_globals():
    ...
```

`_checker = CompatibilityChecker()`는 남기되, `_car_from_globals()`는 더 이상 필요 없으므로 삭제.

#### (b) `is_valid_check`, `test_produced_car`, `run_produced_car` — 전역 대신 `car` 인자를 받도록 변경

```python
def is_valid_check(car):
    return _checker.check(car).passed


def run_produced_car(car):
    if not is_valid_check(car):
        print("자동차가 동작되지 않습니다")
        return
    if car.engine == Engine.BROKEN:
        print("엔진이 고장나있습니다.")
        print("자동차가 움직이지 않습니다.")
        return

    print(f"Car Type : {car.car_type.label}")
    print(f"Engine   : {car.engine.label}")
    print(f"Brake    : {car.brake.label}")
    print(f"Steering : {car.steering.label}")
    print("자동차가 동작됩니다.")


def test_produced_car(car):
    result = _checker.check(car)
    if result.passed:
        print("PASS")
    else:
        print(f"FAIL\n{result.reason}")
```

`run_produced_car`의 4개 `if/elif` 출력 블록을 Step 1에서 만든 `label` 프로�티로 대체했다.
문자열 값(`"Sedan"`, `"GM"`, `"Mando"`, `"Bosch"` 등)은 기존 출력과 **완전히 동일**하므로
회귀 없음 (아래 4.3 characterization 테스트로 확인).

#### (c) `select_car_type` / `select_engine` — `builder`를 받아 상태를 위임하고, 표시 문구는 그대로 유지

```python
def select_car_type(builder, a):
    builder.set_car_type(a)
    print(f"차량 타입으로 {builder.car.car_type.label}을 선택하셨습니다.")


def select_engine(builder, a):
    builder.set_engine(a)
    engine = builder.car.engine
    if engine == Engine.BROKEN:
        print("고장난 엔진을 선택하셨습니다.")
    else:
        print(f"{engine.label} 엔진을 선택하셨습니다.")
```

`select_car_type`은 `label`이 그대로 기존 문구("Sedan", "SUV", "Truck")와 일치해 그대로 대체 가능했다.
`select_engine`은 `Engine.BROKEN.label`이 `"고장난 엔진"`이라서 `f"{label} 엔진을 선택하셨습니다."`로
합치면 `"고장난 엔진 엔진을 선택하셨습니다."`처럼 "엔진"이 중복된다. 그래서 `BROKEN`만 예외 처리했다.

#### (d) `select_brake` / `select_steering` — 표기 불일치는 원본 버그로 판단, `label`로 통일

리팩토링 중 발견한 대소문자 불일치(제동장치/조향장치의 "선택 확인 메시지"가 대문자, "완성 후
요약(RUN 화면)"은 혼합표기)는 사용자 확인 결과 **의도된 표기가 아니라 원본의 버그**로 판정했다.
따라서 이번 단계에서 그대로 두지 않고, `CarType`/`Engine`과 동일하게 `label`로 통일한다.

```python
def select_brake(builder, a):
    builder.set_brake(a)
    print(f"{builder.car.brake.label} 제동장치를 선택하셨습니다.")


def select_steering(builder, a):
    builder.set_steering(a)
    print(f"{builder.car.steering.label} 조향장치를 선택하셨습니다.")
```

**표기가 바뀌는 문구 (의도적인 동작 변경, 버그 수정):**

| 부품 | 변경 전 | 변경 후 |
|---|---|---|
| 제동장치 | `MANDO 제동장치를 선택하셨습니다.` | `Mando 제동장치를 선택하셨습니다.` |
| 제동장치 | `CONTINENTAL 제동장치를 선택하셨습니다.` | `Continental 제동장치를 선택하셨습니다.` |
| 제동장치 | `BOSCH 제동장치를 선택하셨습니다.` | `Bosch 제동장치를 선택하셨습니다.` |
| 조향장치 | `BOSCH 조향장치를 선택하셨습니다.` | `Bosch 조향장치를 선택하셨습니다.` |
| 조향장치 | `MOBIS 조향장치를 선택하셨습니다.` | `Mobis 조향장치를 선택하셨습니다.` |

RUN 요약 화면(`Brake : Mando` 등)은 변경 없음 — 이제 확인 메시지와 요약 화면이 동일한
`label`을 공유하므로 두 화면의 표기가 항상 일치함이 보장된다.

#### (e) `main()` — `q0~q3`/`step` 대신 `builder` 하나만 사용

```python
def main():
    builder = CarBuilder()
    while True:
        step = builder.current_step
        show_menu(step)
        buf = input("INPUT > ").strip()

        if buf == "exit":
            print("바이바이")
            break

        try:
            ans = int(buf)
        except:
            print("ERROR :: 숫자만 입력 가능")
            delay(800)
            continue

        if not is_valid_range(step, ans):
            delay(800)
            continue

        if ans == 0:
            builder.back()
            continue

        if step == 0:
            select_car_type(builder, ans)
            delay(800)
        elif step == 1:
            select_engine(builder, ans)
            delay(800)
        elif step == 2:
            select_brake(builder, ans)
            delay(800)
        elif step == 3:
            select_steering(builder, ans)
            delay(800)
        elif step == 4:
            if ans == 1:
                run_produced_car(builder.car)
                delay(2000)
            elif ans == 2:
                print("Test...")
                delay(1500)
                test_produced_car(builder.car)
                delay(2000)
```

- `step = step + 1`을 각 분기 끝에서 수동으로 하던 부분이 전부 사라졌다. 다음 반복문에서
  `builder.current_step`을 다시 계산하면 방금 채운 필드를 반영해 자동으로 다음 단계가 나온다.
  → "부품은 채웠는데 step 갱신을 깜빡해서 화면이 안 넘어가는" 부류의 버그가 구조적으로 불가능해짐.
- `ans == 0` 처리가 `builder.back()` 한 줄로 줄었다 (기존의 `if step==4: step=0 elif step>0: ...`
  분기가 `CarBuilder` 내부로 이동).

## 4. 테스트

### 4.1 `tests/domain/test_car_builder.py`

```python
import pytest

from domain.car_builder import CarBuilder
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


def test_starts_at_step_zero_and_incomplete():
    builder = CarBuilder()
    assert builder.current_step == 0
    assert builder.is_complete is False


def test_each_set_advances_the_step():
    builder = CarBuilder()
    builder.set_car_type(1)
    assert builder.current_step == 1
    builder.set_engine(1)
    assert builder.current_step == 2
    builder.set_brake(1)
    assert builder.current_step == 3
    builder.set_steering(1)
    assert builder.current_step == 4
    assert builder.is_complete is True


def test_set_stores_enum_values_on_car():
    builder = CarBuilder()
    builder.set_car_type(2)
    assert builder.car.car_type == CarType.SUV


def test_back_from_step_zero_is_a_no_op():
    builder = CarBuilder()
    builder.back()
    assert builder.current_step == 0


@pytest.mark.parametrize("advance_to_step,expected_after_back", [
    (1, 0),
    (2, 1),
    (3, 2),
])
def test_back_decrements_one_step_and_clears_that_field(advance_to_step, expected_after_back):
    builder = CarBuilder()
    setters = [builder.set_car_type, builder.set_engine, builder.set_brake, builder.set_steering]
    for setter in setters[:advance_to_step]:
        setter(1)
    builder.back()
    assert builder.current_step == expected_after_back


def test_back_from_finish_screen_resets_everything():
    builder = CarBuilder()
    builder.set_car_type(1)
    builder.set_engine(1)
    builder.set_brake(1)
    builder.set_steering(1)
    assert builder.current_step == 4

    builder.back()

    assert builder.current_step == 0
    assert builder.car.car_type is None
    assert builder.car.engine is None
    assert builder.car.brake is None
    assert builder.car.steering is None


def test_reselecting_after_back_overwrites_previous_choice():
    builder = CarBuilder()
    builder.set_engine(2)  # 실수로 TOYOTA 선택 (car_type 없이 직접 세팅해도 무방 — builder 단위 테스트)
    builder.back()
    builder.set_engine(3)
    assert builder.car.engine == Engine.WIA
```

### 4.2 `tests/test_assembly_characterization.py` 갱신

Step 2에서 만든 이 테스트는 `assembly.q0 = ...` 식으로 전역 변수를 직접 조작했다. 전역 변수가
사라졌으므로, `Car`를 직접 구성해 함수에 전달하는 방식으로 바꾼다.

```python
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
```

`test_run_produced_car_*` 두 개는 Step 2까지는 없던 신규 테스트다 — 이번 단계에서
`run_produced_car`의 출력 로직이 `label` 기반으로 바뀌었으므로, 이 변경이 실제로 안전한지
검증하려면 회귀 테스트가 필요하다.

## 5. 완료 조건 (Definition of Done)

- [ ] `domain/car_builder.py` 생성, `tests/domain/test_car_builder.py` 전부 통과
- [ ] `assembly.py`에서 `q0, q1, q2, q3, q4`와 `CarType_Q/Engine_Q/brakeSystem_Q/SteeringSystem_Q/Run_Test`,
      그리고 죽은 매직넘버 상수(`SEDAN` 등 11개) 전부 삭제
- [ ] `is_valid_check`, `run_produced_car`, `test_produced_car`가 `car` 인자를 받도록 시그니처 변경
- [ ] `select_car_type/engine/brake/steering`이 `builder` 인자를 받아 `CarBuilder`에 위임
- [ ] `main()`이 `builder = CarBuilder()` 하나만으로 상태를 관리 (로컬 `step` 변수는
      `builder.current_step`에서 매번 다시 계산)
- [ ] `tests/test_assembly_characterization.py`를 `Car` 직접 생성 방식으로 갱신, 전부 통과
- [x] `python assembly.py`로 정상 플로우 + 뒤로가기(각 단계 + 완성 화면에서) + exit 시나리오
      수동 확인. 제동장치/조향장치 확인 메시지는 사용자 확인에 따라 원본 버그로 판정되어
      `label` 표기로 통일됨(3.2(d) 참고) — 그 외 화면 출력은 Step 1/2 때와 완전히 동일

## 6. Non-goals (이 단계에서 하지 않는 것)

- `show_menu`, `is_valid_range`의 `step` 기반 if/elif 체인을 `AssemblyStep` Enum 등으로
  교체하는 것 → Step 4 (`ConsoleView`)
- `input()` 루프 자체를 `AssemblyController` 클래스로 분리하는 것 → Step 4
- `test_assembly.py`(전부 `assert False`인 구식 스텁 파일) 삭제 → Step 5

## 7. 다음 단계와의 연결

Step 4에서 `show_menu`/`is_valid_range`를 `AssemblyStep` Enum 기반의 `ConsoleView`로, `main()`의
입력 루프를 `AssemblyController`로 분리할 때 `CarBuilder`와 `CompatibilityChecker`는 수정 없이
그대로 주입받아 재사용된다 — 이번 단계에서 도메인 로직과 CLI 로직의 경계(“무엇을 파라미터로
주고받는가”)를 먼저 확정해 둔 덕분에 Step 4는 순수하게 “입출력 방식”만 재구성하면 된다.
