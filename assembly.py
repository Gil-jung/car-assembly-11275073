import time
import sys

CLEAR_SCREEN = "\033[H\033[2J"

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

def select_car_type(a):
    global q0
    q0 = a
    if a == 1:
        print("차량 타입으로 Sedan을 선택하셨습니다.")
    elif a == 2:
        print("차량 타입으로 SUV을 선택하셨습니다.")
    elif a == 3:
        print("차량 타입으로 Truck을 선택하셨습니다.")

def select_engine(a):
    global q1
    q1 = a
    if a == 1:
        print("GM 엔진을 선택하셨습니다.")
    elif a == 2:
        print("TOYOTA 엔진을 선택하셨습니다.")
    elif a == 3:
        print("WIA 엔진을 선택하셨습니다.")
    elif a == 4:
        print("고장난 엔진을 선택하셨습니다.")

def select_brake(a):
    global q2
    q2 = a
    if a == 1:
        print("MANDO 제동장치를 선택하셨습니다.")
    elif a == 2:
        print("CONTINENTAL 제동장치를 선택하셨습니다.")
    elif a == 3:
        print("BOSCH 제동장치를 선택하셨습니다.")

def select_steering(a):
    global q3
    q3 = a
    if a == 1:
        print("BOSCH 조향장치를 선택하셨습니다.")
    elif a == 2:
        print("MOBIS 조향장치를 선택하셨습니다.")

def is_valid_check():
    if q0 == SEDAN and q2 == CONTINENTAL:
        return False
    if q0 == SUV and q1 == TOYOTA:
        return False
    if q0 == TRUCK and q1 == WIA:
        return False
    if q0 == TRUCK and q2 == MANDO:
        return False
    if q2 == BOSCH_B and q3 != BOSCH_S:
        return False
    return True

def run_produced_car():
    if not is_valid_check():
        print("자동차가 동작되지 않습니다")
        return
    if q1 == 4:
        print("엔진이 고장나있습니다.")
        print("자동차가 움직이지 않습니다.")
        return

    if q0 == 1:
        print("Car Type : Sedan")
    elif q0 == 2:
        print("Car Type : SUV")
    elif q0 == 3:
        print("Car Type : Truck")

    if q1 == 1:
        print("Engine   : GM")
    elif q1 == 2:
        print("Engine   : TOYOTA")
    elif q1 == 3:
        print("Engine   : WIA")

    if q2 == 1:
        print("Brake    : Mando")
    elif q2 == 2:
        print("Brake    : Continental")
    elif q2 == 3:
        print("Brake    : Bosch")

    if q3 == 1:
        print("Steering : Bosch")
    elif q3 == 2:
        print("Steering : Mobis")

    print("자동차가 동작됩니다.")

def test_produced_car():
    if q0 == SEDAN and q2 == CONTINENTAL:
        print("FAIL\nSedan에는 Continental제동장치 사용 불가")
    elif q0 == SUV and q1 == TOYOTA:
        print("FAIL\nSUV에는 TOYOTA엔진 사용 불가")
    elif q0 == TRUCK and q1 == WIA:
        print("FAIL\nTruck에는 WIA엔진 사용 불가")
    elif q0 == TRUCK and q2 == MANDO:
        print("FAIL\nTruck에는 Mando제동장치 사용 불가")
    elif q2 == BOSCH_B and q3 != BOSCH_S:
        print("FAIL\nBosch제동장치에는 Bosch조향장치 이외 사용 불가")
    else:
        print("PASS")

def main():
    step = 0
    while True:
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
            if step == 4:
                step = 0
            elif step > 0:
                step = step - 1
            continue

        if step == 0:
            select_car_type(ans)
            delay(800)
            step = 1
        elif step == 1:
            select_engine(ans)
            delay(800)
            step = 2
        elif step == 2:
            select_brake(ans)
            delay(800)
            step = 3
        elif step == 3:
            select_steering(ans)
            delay(800)
            step = 4
        elif step == 4:
            if ans == 1:
                run_produced_car()
                delay(2000)
            elif ans == 2:
                print("Test...")
                delay(1500)
                test_produced_car()
                delay(2000)

if __name__ == "__main__":
    main()