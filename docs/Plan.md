# 자동차 조립 시뮬레이터 리팩토링 계획

## 1. 현재 구조 분석

### 1.1 흐름
`차량 타입 선택 → 엔진 선택 → 제동장치 선택 → 조향장치 선택 → RUN/Test` 를
`main()` 안의 `step`(0~4) 값과 전역 변수 `q0~q4`로 관리하는 상태 머신.

### 1.2 문제점

| # | 문제 | 위치 |
|---|------|------|
| P1 | 차량 상태(`q0~q3`)가 모듈 전역 변수. 여러 대의 차량을 동시에 다룰 수 없고, 테스트 시 상태 격리 불가 | 전역 `q0~q3` |
| P2 | 타입/부품 값이 매직 넘버(`1,2,3`)로 표현되어 가독성·안전성 낮음 | `SEDAN=1`, `GM=1` 등 |
| P3 | **호환성 규칙이 두 곳에 중복 구현**됨 (`is_valid_check()` vs `test_produced_car()`). 규칙이 바뀌면 두 곳을 다 고쳐야 하고, 이미 미묘하게 조건 순서/메시지가 다름 → 버그 온상 | L142-153, L192-204 |
| P4 | 출력(print)·입력 검증·상태 변경·비즈니스 로직이 한 함수 안에 뒤섞여 있어 단위 테스트 불가능 (표준출력을 캡처해야만 검증 가능) | `select_*`, `run_produced_car`, `test_produced_car` |
| P5 | `show_menu`, `is_valid_range` 가 `step`(정수) 기준 if-elif 체인으로 분기 → 새 단계 추가 시 여러 함수를 동시에 수정해야 함 (Open-Closed 위반) | `show_menu`, `is_valid_range` |
| P6 | 부품 이름 문자열("GM", "MANDO" 등)이 여러 곳에 하드코딩되어 오탈자/불일치 위험 | `select_*`, `run_produced_car` |
| P7 | `test_assembly.py`가 전부 `assert False` 스텁 — 실제로는 아무것도 검증하지 못함. 현재 구조상 전역 상태 + print 부작용 때문에 제대로 된 단위 테스트 작성이 애초에 어려움 | 전체 |
| P8 | CLI 입출력(input/print/sleep)과 도메인 로직이 강결합되어 있어, 추후 GUI/API 등 다른 인터페이스로 확장 불가능 | `main()` 전체 |

---

## 2. 목표 아키텍처 (OOP)

```
domain/
  parts.py        - CarType, Engine, BrakeSystem, SteeringSystem (Enum + 카탈로그)
  car.py          - Car (선택된 부품을 담는 값 객체)
  compatibility.py- CompatibilityRule(추상) + 구체 규칙들 + CompatibilityChecker
  car_builder.py   - CarBuilder (단계별로 부품을 채워나가는 빌더, 뒤로가기 지원)

cli/
  steps.py        - AssemblyStep(Enum) + 각 스텝의 메뉴 텍스트/유효 범위를 캡슐화
  view.py         - ConsoleView (화면 출력 전담, 도메인 몰라도 됨)
  controller.py   - AssemblyController (입력 루프, View/Builder/Checker 오케스트레이션)

main.py           - entry point (AssemblyController 생성 후 run())
```

### 2.1 도메인 레이어

- **`CarType`, `Engine`, `BrakeSystem`, `SteeringSystem`**: `Enum` 으로 정의 (`SEDAN`, `GM`, `MANDO` ...).
  각 Enum에 표시용 한글 이름을 매핑해 P2, P6 해결.
- **`Car`**: `@dataclass`. `car_type`, `engine`, `brake`, `steering` 필드만 가진 불변 값 객체.
  전역 변수 `q0~q3` 대체 → P1 해결.
- **`CompatibilityRule`**: 규칙 하나 = `(설명, 위반조건 함수)`. 예)
  ```python
  RULES = [
      CompatibilityRule(
          "Sedan에는 Continental 제동장치 사용 불가",
          lambda car: car.car_type == CarType.SEDAN and car.brake == BrakeSystem.CONTINENTAL,
      ),
      ...
  ]
  ```
- **`CompatibilityChecker.check(car) -> CheckResult(passed: bool, reason: str | None)`**:
  `run_produced_car`와 `test_produced_car`가 **동일한 이 객체 하나만** 호출하도록 통일 → P3 해결.
- **`CarBuilder`**: `set_car_type/set_engine/set_brake/set_steering/back()` 등의 메서드로 단계적으로 `Car`를 완성.
  완성 여부(`is_complete`)와 현재 진행 단계도 이 객체가 관리 → step 전역 변수 제거.

### 2.2 CLI 레이어

- **`AssemblyStep`**: `Enum`으로 `CAR_TYPE, ENGINE, BRAKE, STEERING, FINISH`. 각 스텝에 메뉴 텍스트와
  유효 입력 범위를 딕셔너리/클래스로 매핑 → P5 해결 (새 단계 추가 시 이 매핑에만 추가).
- **`ConsoleView`**: `show_menu(step)`, `print_message(text)`, `clear()`, `delay(ms)` 등 순수 출력 담당.
  도메인 객체를 받아 표시 문자열만 만들고 print 부작용은 여기로 격리 → P4 해결.
- **`AssemblyController`**: `input()` 루프, `CarBuilder`/`CompatibilityChecker`/`ConsoleView`를 조합해
  기존 `main()`의 역할 수행. 순수 로직(빌더, 체커)은 컨트롤러 없이도 단독 테스트 가능.

### 2.3 테스트 전략 (P7 해결)

리팩토링 후에는 `input()`/`print()` 없이도 아래가 직접 테스트 가능해짐:
- `CompatibilityChecker` : 5가지 조합에 대해 `check()` 결과 검증 (테이블 기반 테스트로 `run`/`test` 로직 중복도 자연히 제거됨을 검증)
- `CarBuilder` : 단계 진행/뒤로가기/완성 여부
- `ConsoleView` : `capsys`로 출력 스냅샷만 최소 검증 (얇은 레이어이므로 커버리지 낮아도 무방)
- `AssemblyController` : `input()`을 mock하여 시나리오(정상 흐름, 잘못된 입력, 뒤로가기, exit) e2e 검증

`test_assembly.py`의 `assert False` 스텁은 삭제하고, 위 구조에 맞춰 새로 작성.

---

## 3. 단계별 진행 계획

1. **도메인 모델 도입**: `CarType/Engine/BrakeSystem/SteeringSystem` Enum, `Car` dataclass 작성 (기존 로직 변경 없이 병행 가능)
2. **호환성 규칙 통합**: `CompatibilityRule`/`CompatibilityChecker` 작성 후 `is_valid_check`, `test_produced_car`의 중복 로직 제거하고 이걸로 대체 (P3 최우선 해결)
3. **CarBuilder 도입**: 전역 `q0~q3`, `step` 제거하고 빌더로 상태 이전
4. **CLI 분리**: `ConsoleView`/`AssemblyController`로 `main()` 해체
5. **테스트 작성**: 도메인 레이어부터 단위 테스트, 이후 컨트롤러 통합 테스트
6. **기존 `assembly.py`/`test_assembly.py` 제거 및 새 구조로 교체**, `main.py`에서 실행

## 4. 리스크 / 주의사항

- 콘솔 출력 문구(사용자에게 보이는 한글 메시지)는 기존과 최대한 동일하게 유지해 동작 회귀가 없는지 눈으로 확인 필요
- `is_valid_check()`와 `test_produced_car()`의 조건 순서가 미묘하게 다르면 통합 시 어느 쪽이 "정답"인지 결정 필요 (현재는 로직상 동일해 보이나 확인 필요)
- 뒤로가기(`ans==0`) 시 이전에 선택한 부품 값을 유지할지 초기화할지 현재 코드 기준(유지)으로 그대로 이전
