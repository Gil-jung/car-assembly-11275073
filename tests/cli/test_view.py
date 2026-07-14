from cli.steps import AssemblyStep
from cli.view import ConsoleView


def test_show_menu_prints_menu_lines_and_separator(capsys):
    view = ConsoleView()
    view.show_menu(AssemblyStep.STEERING)
    out = capsys.readouterr().out
    assert "어떤 조향장치를 선택할까요?" in out
    assert out.strip().endswith("===============================")


def test_print_message_just_prints(capsys):
    ConsoleView().print_message("hello")
    assert capsys.readouterr().out.strip() == "hello"
