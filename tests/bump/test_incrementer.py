import pytest

from clishelf.bump.incremeters import NumericIncrementer, ValuesIncrementer


def test_numeric_init_wo_first_value():
    func = NumericIncrementer()
    assert func.first_value == "0"
    assert repr(func) == "NumericIncrementer(first_value='0')"


def test_numeric_init_w_first_value():
    func = NumericIncrementer(first_value="5")
    assert func.first_value == "5"
    assert repr(func) == "NumericIncrementer(first_value='5')"

    with pytest.raises(ValueError):
        func.bump("a1")


def test_numeric_init_non_numeric_first_value():
    with pytest.raises(ValueError):
        NumericIncrementer(first_value="a")


def test_numeric_bump_simple_number():
    func = NumericIncrementer()
    assert func.bump("0") == "1"


def test_numeric_bump_prefix_and_suffix():
    func = NumericIncrementer()
    assert func.bump("v0b") == "v1b"
    assert func.bump("r3") == "r4"
    assert func.bump("r3-001") == "r4-001"


def test_numeric_bump_invalid_format():
    func = NumericIncrementer()

    with pytest.raises(ValueError):
        func.bump("foo")


def test_values_init():
    func = ValuesIncrementer([0, 1, 2])
    assert func.optional_value == 0
    assert func.first_value == 0
    assert (
        repr(func)
        == "ValuesIncrementer(values=[0, 1, 2], first_value=0, optional_value=0)"
    )


def test_values_init_w_correct_optional_value():
    func = ValuesIncrementer([0, 1, 2], optional_value=1)
    assert func.optional_value == 1
    assert func.first_value == 0


def test_values_init_w_correct_first_value():
    func = ValuesIncrementer([0, 1, 2], first_value=1)
    assert func.optional_value == 0
    assert func.first_value == 1


def test_values_init_w_correct_optional_and_first_value():
    func = ValuesIncrementer([0, 1, 2], optional_value=0, first_value=1)
    assert func.optional_value == 0
    assert func.first_value == 1


def test_values_init_w_empty_values():
    with pytest.raises(ValueError):
        ValuesIncrementer([])


def test_values_init_w_incorrect_optional_value():
    with pytest.raises(ValueError):
        ValuesIncrementer([0, 1, 2], optional_value=3)


def test_values_init_w_incorrect_first_value():
    with pytest.raises(ValueError):
        ValuesIncrementer([0, 1, 2], first_value=3)


def test_values_bump():
    func = ValuesIncrementer([0, 5, 10])
    assert func.bump(0) == 5


def test_values_bump_raise():
    func = ValuesIncrementer([0, 5, 10])
    with pytest.raises(ValueError):
        func.bump(10)

    with pytest.raises(ValueError):
        func.bump(11)

    func = ValuesIncrementer(["alpha", "beta", "rc", "final"])
    with pytest.raises(ValueError):
        func.bump("final")
