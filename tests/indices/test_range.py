import pytest

from hml.indices.range import RangeIndex


def test_init():
    index = RangeIndex()
    assert index.start is None
    assert index.stop is None
    assert index._value == slice(None)

    index = RangeIndex(start=0, stop=10)
    assert index.start == 0
    assert index.stop == 10
    assert index._value == slice(0, 10)


def test_special_method_repr():
    index = RangeIndex()
    assert repr(index) == "RangeIndex(value=slice(None, None, None))"


def test_property_value():
    index = RangeIndex()
    assert index.value == slice(None)


def test_method_to_str():
    index = RangeIndex()
    assert index.to_str() == ""

    index = RangeIndex(stop=10)
    assert index.to_str() == ":10"

    index = RangeIndex(start=0)
    assert index.to_str() == "0:"

    index = RangeIndex(start=0, stop=10)
    assert index.to_str() == "0:10"


def test_classmethod_from_str():
    index = RangeIndex.from_str("")
    assert index.start is None
    assert index.stop is None
    assert index._value == slice(None)

    with pytest.raises(ValueError):
        RangeIndex.from_str("invalid_string")
    with pytest.raises(ValueError):
        RangeIndex.from_str("0:1:2")
    with pytest.raises(ValueError):
        RangeIndex.from_str("x:1")

    index = RangeIndex.from_str("0:10")
    assert index.start == 0
    assert index.stop == 10
    assert index._value == slice(0, 10)


def test_property_config():
    index = RangeIndex()
    assert index.config == {"start": None, "stop": None}


def test_classmethod_from_config():
    index = RangeIndex.from_config({"start": None, "stop": None})
    assert index.start is None
    assert index.stop is None
    assert index._value == slice(None)
