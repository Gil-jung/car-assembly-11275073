# 자동차 조립 시뮬레이터 리팩토링 요약

`차량 타입 선택 → 부품(엔진/제동장치/조향장치) 선택 → 완성된 차량 RUN/Test` 흐름의
절차지향 CLI 스크립트(`assembly.py`)를, 전역 변수와 매직 넘버 없이 도메인 로직과 CLI를
분리한 객체지향 구조로 5단계에 걸쳐 리팩토링했다. 상세 설계·구현 근거는 [Plan.md](./Plan.md)와
[step1.md](./step1.md)~[step5.md](./step5.md)에 있다.

## 리팩토링 전/후

| | 리팩토링 전 (`assembly.py`) | 리팩토링 후 |
|---|---|---|
| 상태 관리 | 모듈 전역 변수 `q0~q3`, `main()` 로컬 `step` | `CarBuilder`가 불변 `Car` 값 객체를 소유, `current_step`을 그로부터 계산 |
| 부품/타입 표현 | 매직 넘버(`SEDAN=1`, `GM=1` ...) | `CarType`/`Engine`/`BrakeSystem`/`SteeringSystem` Enum (+ `label`) |
| 호환성 규칙 | `is_valid_check()`와 `test_produced_car()`에 동일 규칙이 중복 구현 | `CompatibilityRule`/`CompatibilityChecker`로 단일화 (SSOT) |
| 화면 분기 | `step` 정수 기준 if-elif 체인 (`show_menu`, `is_valid_range`) | `AssemblyStep` Enum + `MENUS`/`INPUT_RANGES` 테이블 |
| 입출력/로직 결합 | `input()`/`print()`/`time.sleep()`이 도메인 로직과 한 함수에 혼재 | `domain/`(순수 로직) ↔ `cli/`(입출력)로 분리, `AssemblyController`가 조립 |
| 테스트 | `test_assembly.py` 전부 `assert False` 스텁 | `tests/domain/`, `tests/cli/` 48개 테스트, `input()` 몬키패치로 전체 흐름 E2E 검증 가능 |

## 발견된 문제(P1~P8)와 해소 현황

| # | 문제 | 해소 방법 | 해소 단계 |
|---|---|---|---|
| P1 | 차량 상태가 전역 변수 | `CarBuilder`가 `Car` 값 객체 소유 | [Step 1](./step1.md)(모델), [Step 3](./step3.md)(전역 제거) |
| P2 | 매직 넘버 | Enum 도입 | Step 1(도입), Step 3(구 상수 삭제) |
| P3 | 호환성 규칙 중복 구현 | `CompatibilityChecker`로 단일화 | [Step 2](./step2.md) |
| P4 | 출력/검증/로직 혼재로 테스트 불가 | 도메인 계층은 print 없이 순수 로직만 수행 | Step 1~3 |
| P5 | `step` 기준 if-elif 체인 (OCP 위반) | `AssemblyStep` + 데이터 테이블 | [Step 4](./step4.md) |
| P6 | 부품 이름 문자열 하드코딩/불일치 | `label` 프로퍼티로 단일화 (원본의 대소문자 표기 버그도 수정) | Step 1(정의), Step 3(적용+버그 수정) |
| P7 | 테스트 스텁이 전부 `assert False` | `tests/domain/`, `tests/cli/`로 대체 | Step 1~4(작성), [Step 5](./step5.md)(스텁 삭제) |
| P8 | CLI와 도메인 로직 강결합 | `domain/` ↔ `cli/` 분리 | Step 4 |

## 최종 구조

```
domain/
  parts.py           - CarType, Engine, BrakeSystem, SteeringSystem (Enum)
  car.py             - Car (불변 값 객체)
  car_builder.py     - CarBuilder (조립 진행 상태 관리, 뒤로가기 포함)
  compatibility.py   - CompatibilityRule, CompatibilityChecker
cli/
  steps.py           - AssemblyStep, MENUS, INPUT_RANGES
  view.py            - ConsoleView (출력 전담)
  controller.py      - AssemblyController (입력 루프 오케스트레이션)
main.py              - 진입점
tests/
  domain/            - 도메인 레이어 단위 테스트
  cli/               - CLI 레이어 단위/E2E 테스트
docs/
  Plan.md, step1~5.md, README.md
```

## 실행 / 테스트

```bash
py main.py          # 실행
py -m pytest -v      # 테스트 (48 passed)
```

## 단계별 문서

1. [Plan.md](./Plan.md) — 초기 분석 및 전체 리팩토링 계획
2. [step1.md](./step1.md) — 도메인 모델 도입 (Enum, `Car`)
3. [step2.md](./step2.md) — 호환성 규칙 통합 (`CompatibilityChecker`)
4. [step3.md](./step3.md) — 전역 상태 제거 (`CarBuilder`)
5. [step4.md](./step4.md) — CLI 분리 (`AssemblyStep`/`ConsoleView`/`AssemblyController`)
6. [step5.md](./step5.md) — 컷오버 (구 구조 삭제, `main.py` 단일 진입점 확정)
