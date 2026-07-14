# Step 1. 도메인 모델 도입 (Enum + Car 값 객체)

> Plan.md 3장 "단계별 진행 계획"의 1단계에 대한 상세 작업 명세.
> 이 단계에서는 `assembly.py`의 기존 동작을 전혀 바꾸지 않는다. 새 도메인 모듈만 추가하고,
> 그 모듈에 대한 단위 테스트만 작성한다. (`assembly.py`를 이 모듈로 교체하는 작업은 Step 3에서 진행)

## 1. 목표

기존 `assembly.py`의 매직 넘버 상수(`SEDAN=1`, `GM=1`, `MANDO=1` ...)와, 그 값들을 담던 전역 변수
`q0~q3`를 대체할 **도메인 모델**을 새로 만든다. 아직 기존 코드와 연결하지 않고 독립적으로
완성 + 테스트한다.

## 2. 대상 파일 (신규 생성)

```
domain/
  __init__.py
  parts.py     # CarType, Engine, BrakeSystem, SteeringSystem
  car.py       # Car dataclass
tests/
  domain/
    test_parts.py
    test_car.py
```

## 3. 세부 작업

### 3.1 `domain/parts.py` — 부품 Enum 정의

기존 매핑을 그대로 값으로 유지해 리팩토링 중간에 값이 어긋나지 않도록 한다.

| 기존 상수 | 값 | 대체할 Enum 멤버 |
|---|---|---|
| `SEDAN` | 1 | `CarType.SEDAN` |
| `SUV` | 2 | `CarType.SUV` |
| `TRUCK` | 3 | `CarType.TRUCK` |
| `GM` | 1 | `Engine.GM` |
| `TOYOTA` | 2 | `Engine.TOYOTA` |
| `WIA` | 3 | `Engine.WIA` |
| (고장난 엔진) | 4 | `Engine.BROKEN` |
| `MANDO` | 1 | `BrakeSystem.MANDO` |
| `CONTINENTAL` | 2 | `BrakeSystem.CONTINENTAL` |
| `BOSCH_B` | 3 | `BrakeSystem.BOSCH` |
| `BOSCH_S` | 1 | `SteeringSystem.BOSCH` |
| `MOBIS` | 2 | `SteeringSystem.MOBIS` |

각 Enum 멤버는 화면 출력용 한글 라벨을 함께 갖도록 `label` 프로퍼티를 추가한다
(기존 `select_*`, `run_produced_car`의 print 문에 흩어져 있던 문자열을 한 곳으로 모음 → Plan.md P2, P6 해결).

```python
# domain/parts.py
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
```

> 주의: `BrakeSystem.BOSCH`와 `SteeringSystem.BOSCH`는 이름은 같지만 값(3 vs 1)과 타입이 다른
> **서로 다른 Enum 멤버**다. 기존 코드에서 `q2 == BOSCH_B and q3 != BOSCH_S` 처럼 서로 다른
> 상수를 이름만 보고 혼동하기 쉬웠던 부분(P2)이 Enum 타입 분리로 원천 차단된다.

### 3.2 `domain/car.py` — Car 값 객체

```python
# domain/car.py
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
```

- `frozen=True` : 값 객체는 불변으로 두고, 부품을 하나씩 채워나가는 로직(Builder)은
  Step 3에서 `Car(**{**asdict(car), "engine": new_engine})` 형태로 "새 Car를 반환"하는 방식으로 처리한다.
  (전역 변수 `q0~q3`를 직접 mutate하던 기존 방식과 달리, 상태 변경이 항상 새 객체 생성으로 드러나
  추적하기 쉬워짐)
- 4개 필드 모두 `Optional`인 이유: 조립 과정 중간에는 아직 선택되지 않은 부품이 있을 수 있기 때문
  (기존 `q0~q3 = 0` 초기값과 동일한 의도). `is_complete`로 "네 부품이 모두 선택되었는지"를
  한 곳에서 판단 → Step 3의 `CarBuilder`, `AssemblyController`에서 재사용.

## 4. 테스트 (`tests/domain/`)

이 단계는 순수 데이터 구조라 테스트도 단순하다. 목적은 "라벨 매핑 누락"과 "Enum 값 회귀"를
잡는 것.

```python
# tests/domain/test_parts.py
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
    # label 매핑에서 멤버 하나라도 빠지면 KeyError로 즉시 드러나야 한다
    for enum_cls in (CarType, Engine, BrakeSystem, SteeringSystem):
        for member in enum_cls:
            assert isinstance(member.label, str) and member.label
```

```python
# tests/domain/test_car.py
from domain.car import Car
from domain.parts import CarType, Engine, BrakeSystem, SteeringSystem


def test_default_car_is_not_complete():
    car = Car()
    assert car.is_complete is False


def test_partially_filled_car_is_not_complete():
    car = Car(car_type=CarType.SEDAN, engine=Engine.GM)
    assert car.is_complete is False


def test_fully_filled_car_is_complete():
    car = Car(
        car_type=CarType.SEDAN,
        engine=Engine.GM,
        brake=BrakeSystem.MANDO,
        steering=SteeringSystem.BOSCH,
    )
    assert car.is_complete is True


def test_car_is_immutable():
    car = Car(car_type=CarType.SEDAN)
    try:
        car.car_type = CarType.SUV
        assert False, "frozen dataclass는 필드 수정 시 예외를 던져야 한다"
    except AttributeError:
        pass
```

## 5. 완료 조건 (Definition of Done)

- [ ] `domain/parts.py`, `domain/car.py` 생성
- [ ] 위 테스트 전부 통과 (`pytest tests/domain -v`)
- [ ] `assembly.py`는 **아직 수정하지 않음** (기존 동작 100% 유지, 회귀 없음)
- [ ] 기존 `test_assembly.py`의 `assert False` 스텁도 아직 유지 (삭제는 Step 3~5에서 일괄 처리)

## 6. Non-goals (이 단계에서 하지 않는 것)

- 호환성 규칙(`is_valid_check`, `test_produced_car` 중복) 정리 → Step 2
- `q0~q3`/`step` 전역 변수 제거, 빌더 도입 → Step 3
- CLI(`main()`, `show_menu`, `input()`) 분리 → Step 4
- `assembly.py` 삭제/교체 → Step 5 이후

## 7. 다음 단계와의 연결

Step 2(`CompatibilityRule`/`CompatibilityChecker`)는 이 단계에서 만든 `Car`, `CarType`, `Engine`,
`BrakeSystem`, `SteeringSystem`을 인자로 받아 규칙을 판정하는 구조가 된다. 즉 Step 1의 산출물이
Step 2의 입력 타입이 되므로, Enum 이름/값이 여기서 확정되면 이후 단계에서 바꾸지 않는 것을 권장.
