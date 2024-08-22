# setup
from custom_objects import Toy

from hml.saving.serialization import deserialize, serialize


def test_serialize():
    obj = Toy(1, 2)
    expected = {
        "module": "custom_objects",
        "class_name": "Toy",
        "config": {"arg1": 1, "arg2": 2},
    }

    assert serialize(obj) == expected


def test_deserialize():
    serialized_obj = {
        "module": "custom_objects",
        "class_name": "Toy",
        "config": {"arg1": 1, "arg2": 2},
    }

    expected_config = {"arg1": 1, "arg2": 2}

    assert deserialize(serialized_obj).config == expected_config
