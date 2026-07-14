# Step 5. 컷오버 — 구 구조 제거 및 `main.py` 단일 진입점 확정

> Plan.md 3장 "단계별 진행 계획"의 6단계("기존 `assembly.py`/`test_assembly.py` 제거 및
> 새 구조로 교체, `main.py`에서 실행")에 대한 상세 작업 명세이자, 리팩토링 전체의 마무리 단계.
> Step 1~4는 전부 "새 구조를 `assembly.py` 옆에 병행으로 쌓기"만 했고 기존 스크립트는
> 한 줄도 지우지 않았다. 이번 단계에서 그 병행 상태를 끝내고 `cli/`+`domain/`+`main.py`
> 하나로 정리한다.

## 1. 목표

- Step 4에서 이미 `main.py`(`cli/` 기반)가 `assembly.py`와 **완전히 동일한 출력**을 낸다는
  것을 3가지 시나리오로 diff 검증해두었다. 이 검증을 몇 가지 시나리오 더 추가해 최종 확인한 뒤,
  `assembly.py`를 삭제하고 `main.py`를 유일한 실행 스크립트로 확정한다.
- `test_assembly.py`(전부 `assert False`인 스텁 10개)와, `assembly.py`에 의존하던
  `tests/test_assembly_characterization.py`(Step 2~3에서 회귀 방지용으로 썼던 임시 테스트)를
  정리한다. 이 두 파일이 검증하려던 대상은 이제 `tests/domain/`, `tests/cli/`가 더 정확하고
  격리된 방식으로 커버하고 있으므로, 별도 이관 없이 삭제만 하면 된다.
- Plan.md에서 정의한 문제(P1~P8)가 실제로 전부 해소되었는지 최종적으로 표로 확인한다.

## 2. 대상 파일

```
삭제:
  assembly.py
  test_assembly.py
  tests/test_assembly_characterization.py

변경 없음(그대로 유지):
  domain/*, cli/*, main.py, tests/domain/*, tests/cli/*
```

## 3. 세부 작업

### 3.1 삭제 전 — 최종 동등성 검증 (baseline diff)

`assembly.py`를 지우고 나면 더 이상 "구버전과 비교"가 불가능해지므로, 삭제하기 **직전에** 몇 가지
시나리오를 양쪽에서 실행해 출력을 diff로 확인한다 (Step 4에서 이미 3개 시나리오를 확인했지만,
이번이 마지막 기회이므로 전 단계 범위/뒤로가기까지 포함해 더 넓게 확인).

| 시나리오 | 입력 시퀀스 |
|---|---|
| RUN 성공 (Sedan/GM/Mando/Bosch) | `1,1,1,1,1,exit` |
| Test FAIL (Truck+Mando) | `3,3,1,1,2,exit` |
| 엔진 고장 | `1,4,1,1,1,exit` |
| 뒤로가기 — 단계별 재선택 (Sedan→SUV로 정정) | `1,0,2,1,1,1,1,exit` |
| 뒤로가기 — 완성 화면에서 처음으로 | `1,1,1,1,0,2,1,1,1,1,exit` |
| 잘못된 범위 입력 | `9,1,1,1,1,1,exit` |
| 숫자가 아닌 입력 | `abc,1,1,1,1,1,exit` |

```bash
for inputs in "1,1,1,1,1,exit" "3,3,1,1,2,exit" "1,4,1,1,1,exit" \
              "1,0,2,1,1,1,1,exit" "1,1,1,1,0,2,1,1,1,1,exit" \
              "9,1,1,1,1,1,exit" "abc,1,1,1,1,1,exit"; do
  printf '%s' "$inputs" | tr ',' '\n' > /tmp/in.txt
  py main.py < /tmp/in.txt > /tmp/a.txt 2>&1
  py assembly.py < /tmp/in.txt > /tmp/b.txt 2>&1
  diff /tmp/a.txt /tmp/b.txt && echo "OK: $inputs"
done
```

전부 `OK`가 나와야 다음 단계(삭제)로 진행한다. 하나라도 다르면 그 시나리오의 diff를 먼저
분석해서 `cli/` 쪽 구현이 놓친 부분을 고친다 (되돌아가서 Step 4 산출물을 수정).

### 3.2 삭제

```bash
git rm assembly.py test_assembly.py tests/test_assembly_characterization.py
```

- `test_assembly.py`: 10개 테스트 전부 `assert False`로, 애초에 아무 것도 검증하지 못하던
  스텁이었다. 동일 대상(`is_valid_range`, `select_*`, `is_valid_check`, `run_produced_car` 등)은
  이제 `tests/domain/test_car_builder.py`, `tests/domain/test_compatibility.py`,
  `tests/cli/test_controller.py`, `tests/cli/test_steps.py`가 실질적으로 검증하고 있다.
- `tests/test_assembly_characterization.py`: `assembly.py` 함수 시그니처 변화를 추적하며
  Step 2~3 사이의 안전망 역할만 하도록 만든 임시 테스트였다. `assembly.py` 자체가 사라지므로
  같이 제거한다. (동등한 시나리오는 `tests/cli/test_controller.py`의 happy-path/FAIL/broken-engine
  테스트가 커버)

### 3.3 `main.py`를 유일한 진입점으로 확정

이미 Step 4에서 `main.py`는 `AssemblyController().run()`만 호출하는 상태였다. 삭제 후
프로젝트의 유일한 실행 스크립트가 되므로, 실행 방법은 다음으로 정리된다.

```bash
py main.py
```

## 4. 테스트

이 단계는 새 테스트를 추가하지 않는다 — 오히려 더 이상 유효하지 않은 테스트를 제거하는 단계다.
삭제 후 전체 테스트 스위트를 다시 돌려 회귀가 없는지 확인한다.

```bash
py -m pytest -v
```

기대 결과: Step 4까지 있던 `10 failed`(구식 스텁)가 사라지고, `tests/domain`, `tests/cli`의
모든 테스트만 남아 **전부 통과**해야 한다.

## 5. 완료 조건 (Definition of Done)

- [ ] 3.1의 baseline diff 7개 시나리오 전부 `OK` 확인 (삭제 전에 수행)
- [ ] `assembly.py`, `test_assembly.py`, `tests/test_assembly_characterization.py` 삭제
- [ ] `py -m pytest -v` 전체 통과, 실패 0건
- [ ] `py main.py`로 수동 실행해 정상 동작 확인 (이제 비교 대상이 없으므로 육안 확인)
- [ ] 저장소에 `assembly.py`/`test_assembly.py`를 참조하는 곳이 남아있지 않은지 확인
      (`grep -rn "assembly" --include=*.py .` 로 `main.py`/`cli`/`domain`/`tests` 외에
      걸리는 게 없어야 함)

## 6. Non-goals (이 단계에서 하지 않는 것)

- 새로운 기능 추가 없음 — 순수 컷오버(구조 정리)만 수행
- `README`, `pyproject.toml`, 패키징/배포 설정 등은 요청받지 않는 한 만들지 않음
- Step 3에서 남겨둔 "제동장치/조향장치 확인 메시지 표기" 같은 이슈는 이미 Step 3에서 해결됨 —
  이 단계에서 추가로 손댈 문구 이슈는 없음

## 7. 리팩토링 전체 요약 — Plan.md의 문제(P1~P8) 해소 현황

| # | 문제 | 해소 방법 | 해소된 단계 |
|---|---|---|---|
| P1 | 차량 상태가 전역 변수 (`q0~q3`) | `CarBuilder`가 `Car` 값 객체를 소유 | Step 1(모델), Step 3(전역 제거) |
| P2 | 매직 넘버 (`SEDAN=1` 등) | `CarType/Engine/BrakeSystem/SteeringSystem` Enum | Step 1(도입), Step 3(구 상수 완전 삭제) |
| P3 | 호환성 규칙이 두 곳에 중복 구현 | `CompatibilityRule`/`CompatibilityChecker`로 단일화 | Step 2 |
| P4 | 출력/검증/로직 혼재로 단위 테스트 불가 | `Car`/`CarBuilder`/`CompatibilityChecker`는 print 없이 순수 로직만 수행 | Step 1~3 |
| P5 | `step` 기준 if-elif 체인 (OCP 위반) | `AssemblyStep` Enum + `MENUS`/`INPUT_RANGES` 테이블 | Step 4 |
| P6 | 부품 이름 문자열 하드코딩/불일치 | `label` 프로퍼티로 단일화 (원본에 있던 대소문자 버그도 함께 수정) | Step 1(정의), Step 3(적용+버그 수정) |
| P7 | `test_assembly.py`가 전부 `assert False` | `tests/domain/`, `tests/cli/`로 대체, `input()` 몬키패치로 전체 흐름 E2E 테스트 가능 | Step 1~4(테스트 작성), Step 5(스텁 삭제) |
| P8 | CLI와 도메인 로직 강결합 | `domain/`(로직) ↔ `cli/`(입출력) 분리, `AssemblyController`가 조립 | Step 4 |

## 8. 최종 디렉터리 구조

```
domain/
  parts.py           - CarType, Engine, BrakeSystem, SteeringSystem (Enum)
  car.py             - Car (불변 값 객체)
  car_builder.py     - CarBuilder (조립 진행 상태 관리)
  compatibility.py   - CompatibilityRule, CompatibilityChecker
cli/
  steps.py           - AssemblyStep, MENUS, INPUT_RANGES
  view.py            - ConsoleView
  controller.py      - AssemblyController
main.py              - 진입점
tests/
  domain/            - 도메인 레이어 단위 테스트
  cli/               - CLI 레이어 단위/E2E 테스트
docs/
  Plan.md, step1~5.md - 리팩토링 설계 문서
```
