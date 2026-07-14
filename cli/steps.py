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
