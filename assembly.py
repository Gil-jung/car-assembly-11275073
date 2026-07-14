import time
import sys

from domain.car_builder import CarBuilder
from domain.parts import Engine
from domain.compatibility import CompatibilityChecker

CLEAR_SCREEN = "\033[H\033[2J"

_checker = CompatibilityChecker()

def delay(ms):
    t = ms / 1000.0
    time.sleep(t)

def clear():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()

def show_menu(step):
    clear()
    if step == 0:
        print("        ______________")
        print("       /|            |")
        print("  ____/_|_____________|____")
        print(" |                      O  |")
        print(" '-(@)----------------(@)--'")
        print("===============================")
        print("어떤 차량 타입을 선택할까요?")
        print("1. Sedan")
        print("2. SUV")
        print("3. Truck")
    elif step == 1:
        print("어떤 엔진을 탑재할까요?")
        print("0. 뒤로가기")
        print("1. GM")
        print("2. TOYOTA")
        print("3. WIA")
        print("4. 고장난 엔진")
    elif step == 2:
        print("어떤 제동장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. MANDO")
        print("2. CONTINENTAL")
        print("3. BOSCH")
    elif step == 3:
        print("어떤 조향장치를 선택할까요?")
        print("0. 뒤로가기")
        print("1. BOSCH")
        print("2. MOBIS")
    elif step == 4:
        print("멋진 차량이 완성되었습니다.")
        print("0. 처음 화면으로 돌아가기")
        print("1. RUN")
        print("2. Test")
    print("===============================")

def is_valid_range(step, ans):
    if step == 0:
        if ans < 1 or ans > 3:
            print("ERROR :: 차량 타입은 1 ~ 3 범위만 선택 가능")
            return False
    if step == 1:
        if ans < 0 or ans > 4:
            print("ERROR :: 엔진은 1 ~ 4 범위만 선택 가능")
            return False
    if step == 2:
        if ans < 0 or ans > 3:
            print("ERROR :: 제동장치는 1 ~ 3 범위만 선택 가능")
            return False
    if step == 3:
        if ans < 0 or ans > 2:
            print("ERROR :: 조향장치는 1 ~ 2 범위만 선택 가능")
            return False
    if step == 4:
        if ans < 0 or ans > 2:
            print("ERROR :: Run 또는 Test 중 하나를 선택 필요")
            return False
    return True

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

def select_brake(builder, a):
    builder.set_brake(a)
    print(f"{builder.car.brake.label} 제동장치를 선택하셨습니다.")

def select_steering(builder, a):
    builder.set_steering(a)
    print(f"{builder.car.steering.label} 조향장치를 선택하셨습니다.")

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

if __name__ == "__main__":
    main()
