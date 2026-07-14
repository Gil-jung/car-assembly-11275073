from cli.steps import AssemblyStep, MENUS, INPUT_RANGES


def test_every_step_has_a_menu_and_input_range():
    for step in AssemblyStep:
        assert step in MENUS
        assert step in INPUT_RANGES


def test_car_type_step_does_not_allow_back():
    min_value, _, _ = INPUT_RANGES[AssemblyStep.CAR_TYPE]
    assert min_value == 1


def test_other_steps_allow_back():
    for step in (AssemblyStep.ENGINE, AssemblyStep.BRAKE, AssemblyStep.STEERING, AssemblyStep.FINISH):
        min_value, _, _ = INPUT_RANGES[step]
        assert min_value == 0
