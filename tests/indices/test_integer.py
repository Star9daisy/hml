import pytest

from hml.indices.integer import IntegerIndex


def test_init():
    index = IntegerIndex()
    assert index._value == 0

    index = IntegerIndex(value=10)
    assert index._value == 10


def test_special_method_repr():
    index = IntegerIndex()
    assert repr(index) == "IntegerIndex(value=0)"


def test_property_value():
    index = IntegerIndex()
    assert index.value == 0


def test_method_to_str():
    index = IntegerIndex()
    assert index.to_str() == "0"


def test_classmethod_from_str():
    index = IntegerIndex.from_str("10")
    assert index._value == 10

    with pytest.raises(ValueError):
        IntegerIndex.from_str("invalid_string")


def test_property_config():
    index = IntegerIndex()
    assert index.config == {"value": 0}


def test_classmethod_from_config():
    index = IntegerIndex.from_config({"value": 10})
    assert index._value == 10
