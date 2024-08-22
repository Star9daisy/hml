from pathlib import Path

import awkward as ak

from hml.types.utils import (
    array_to_momentum,
    index_to_str,
    pathlike_to_path,
    str_to_index,
)


def test_pathlike_to_path():
    assert pathlike_to_path("test") == Path("test")
    assert pathlike_to_path(Path("test")) == Path("test")


def test_index_to_str():
    assert index_to_str(0) == "0"
    assert index_to_str(slice(None)) == ""
    assert index_to_str(slice(None, 10)) == ":10"
    assert index_to_str(slice(10, None)) == "10:"
    assert index_to_str(slice(10, 20)) == "10:20"


def test_str_to_index():
    assert str_to_index("0") == 0
    assert str_to_index("") == slice(None)
    assert str_to_index(":") == slice(None)
    assert str_to_index(":10") == slice(None, 10)
    assert str_to_index("10:") == slice(10, None)
    assert str_to_index("10:20") == slice(10, 20)


def test_array_to_momentum():
    array = ak.Array([{"pt": 1.0, "py": 2.0, "pz": 3.0, "e": 4.0}])
    array_to_momentum(array)

    array = ak.Array([{"pt": 1.0, "eta": 2.0, "phi": 3.0, "m": 4.0}])
    array_to_momentum(array)
