import sys
import time

from cli.steps import AssemblyStep, MENUS

CLEAR_SCREEN = "\033[H\033[2J"


class ConsoleView:
    def clear(self) -> None:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()

    def delay(self, ms: int) -> None:
        time.sleep(ms / 1000.0)

    def show_menu(self, step: AssemblyStep) -> None:
        self.clear()
        for line in MENUS[step]:
            print(line)
        print("===============================")

    def print_message(self, text: str) -> None:
        print(text)
