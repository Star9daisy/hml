from hml.indices.integer import IntegerIndex
from hml.indices.range import RangeIndex
from hml.indices.utils import deserialize, serialize


def test_serialize():
    index = IntegerIndex()
    assert serialize(index) == {
        "module": "hml.indices.integer",
        "class_name": "IntegerIndex",
        "config": {"value": 0},
    }

    index = RangeIndex()
    assert serialize(index) == {
        "module": "hml.indices.range",
        "class_name": "RangeIndex",
        "config": {"start": None, "stop": None},
    }


def test_deserialize():
    dict_ = {
        "module": "hml.indices.integer",
        "class_name": "IntegerIndex",
        "config": {"value": 0},
    }
    index = deserialize(dict_)
    assert index.value == 0

    dict_ = {
        "module": "hml.indices.range",
        "class_name": "RangeIndex",
        "config": {"start": None, "stop": None},
    }
    index = deserialize(dict_)
    assert index.value == slice(None)
