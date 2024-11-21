import awkward as ak
import pytest
import vector

from hml.types.utils import (
    array_to_momentum,
    index_to_str,
    momentum_to_array,
    pxpypze_to_ptetaphimass,
    str_to_index,
)

vector.register_awkward()


@pytest.fixture
def array():
    return ak.Array(
        [
            {"pt": 3.42, "eta": 1.24, "phi": 1.21, "M": 22.6},
            {"pt": 71.8, "eta": 2.72, "phi": 1.11, "M": 519},
            {"pt": 71.1, "eta": 2.73, "phi": 1.1, "M": 631},
        ],
    )


@pytest.fixture
def momentum():
    return ak.Array(
        [
            {"pt": 3.42, "eta": 1.24, "phi": 1.21, "M": 22.6},
            {"pt": 71.8, "eta": 2.72, "phi": 1.11, "M": 519},
            {"pt": 71.1, "eta": 2.73, "phi": 1.1, "M": 631},
        ],
        with_name="Momentum4D",
    )


@pytest.fixture
def pxpypze_momentum():
    return ak.Array(
        [
            {"px": 1.2, "py": 3.2, "pz": 5.4, "E": 23.5},
            {"px": 32.2, "py": 64.21, "pz": 543.34, "E": 755.12},
            {"px": 32.45, "py": 63.21, "pz": 543.14, "E": 835.56},
        ],
        with_name="Momentum4D",
    )


@pytest.fixture
def ptetaphimass_momentum():
    return ak.Array(
        [
            {
                "pt": 3.417601498127013,
                "eta": 1.2383651522500303,
                "phi": 1.2120256565243244,
                "mass": 22.614375958668415,
            },
            {
                "pt": 71.8314979657253,
                "eta": 2.7209004694132792,
                "phi": 1.1059658021461118,
                "mass": 519.4497999807104,
            },
            {
                "pt": 71.05284371508293,
                "eta": 2.731341597670935,
                "phi": 1.096511490765607,
                "mass": 630.9603374222503,
            },
        ],
        with_name="Momentum4D",
    )


def test_array_to_momentum(array, momentum):
    assert ak.almost_equal(array_to_momentum(array), momentum)


def test_momentum_to_array(momentum, array):
    assert ak.almost_equal(momentum_to_array(momentum), array)


def test_pxpypze_to_ptetaphimass(pxpypze_momentum, ptetaphimass_momentum):
    result = pxpypze_to_ptetaphimass(pxpypze_momentum)

    assert result.fields == ["pt", "eta", "phi", "mass"]
    assert ak.almost_equal(result, ptetaphimass_momentum)


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
