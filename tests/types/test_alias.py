from hml.types import var


def test_var():
    assert str(var) == "var"
    assert repr(var) == "var"
