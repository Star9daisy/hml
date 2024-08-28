# setup
from custom_objects import NSubjettiness

from hml.saving.serialization import deserialize, serialize


def test_serialize():
    obj = NSubjettiness(1, 2)
    expected = {
        "module": "custom_objects",
        "class_name": "NSubjettiness",
        "config": {"m": 1, "n": 2, "name": None},
    }

    assert serialize(obj) == expected


def test_deserialize():
    serialized_obj = {
        "module": "custom_objects",
        "class_name": "NSubjettiness",
        "config": {"m": 1, "n": 2, "name": None},
    }

    expected_config = {"m": 1, "n": 2, "name": None}

    assert deserialize(serialized_obj).config == expected_config
