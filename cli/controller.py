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
