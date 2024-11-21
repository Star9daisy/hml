import awkward as ak
import pytest
import vector

from hml.operations.fastjet import get_inclusive_jets, get_jet_algorithm

vector.register_awkward()


@pytest.fixture
def particles():
    return ak.Array(
        [
            {"px": 1.2, "py": 3.2, "pz": 5.4, "E": 23.5},
            {"px": 32.2, "py": 64.21, "pz": 543.34, "E": 755.12},
            {"px": 32.45, "py": 63.21, "pz": 543.14, "E": 835.56},
        ],
        with_name="Momentum4D",
    )


def test_get_jet_algorithm():
    assert get_jet_algorithm("kt") == 0
    assert get_jet_algorithm("ca") == 1
    assert get_jet_algorithm("ak") == 2

    with pytest.raises(ValueError):
        get_jet_algorithm("unknown")


def test_get_inclusive_jets(particles):
    jets = get_inclusive_jets(particles, "ak", 1.0)

    assert len(jets) == 1
    assert jets.typestr.startswith("1 * Momentum4D")
    assert jets.fields == ["px", "py", "pz", "E"]


def test_get_inclusive_jets_with_constituents(particles):
    _, constituents = get_inclusive_jets(particles, "ak", 1.0, True)

    assert len(constituents) == 1
    assert constituents.typestr.startswith("1 * var * Momentum4D")
    assert constituents.fields == ["px", "py", "pz", "E"]
