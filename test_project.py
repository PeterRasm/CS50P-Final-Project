import pytest
from project import read_argv, calculate_cost, get_miles
from car_class import CAR

# Testing read_argv
def test_read_argv():
    with pytest.raises(SystemExit) as sample:
        # mile instead of miles
        read_argv(["mile:237"])
    assert sample.type == SystemExit
    assert sample.value.code == 6

    with pytest.raises(SystemExit) as sample:
        read_argv(["miles:237", "price:5.0", "miles:732"])
    assert sample.type == SystemExit
    assert sample.value.code == 2

    with pytest.raises(SystemExit) as sample:
        read_argv(["miles:abc"])
    assert sample.type == SystemExit
    assert sample.value.code == 3

    with pytest.raises(SystemExit) as sample:
        read_argv(["price:abc"])
    assert sample.type == SystemExit
    assert sample.value.code == 4

    with pytest.raises(SystemExit) as sample:
        read_argv(["mpg:abc"])
    assert sample.type == SystemExit
    assert sample.value.code == 5

    with pytest.raises(SystemExit) as sample:
        read_argv(["mpg:22"])
    assert sample.type == SystemExit
    assert sample.value.code == 5

    with pytest.raises(SystemExit) as sample:
        read_argv(["mpg:22-25"])
    assert sample.type == SystemExit
    assert sample.value.code == 5


# Testing calculating_cost
def test_calculate_cost():
    assert calculate_cost(10, 2, 0, 5) == 25
    assert calculate_cost(10, 0, 2, 5) == 25

    assert calculate_cost(10, 2, 2, 5) == 25
    assert calculate_cost(10, 2, 3, 5) == 20

# Testing input miles from "user"
def test_get_miles(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "1000")
    assert get_miles() == 1000


# Test car class
def test_class():
    car = CAR.get_newcar("Honda", "Pilot AWD", 2021)
    assert car.mpg_cty == 19
    assert car.mpg_hwy == 26






