import pytest

from hml.observables import parse_observable


def test_parse_observable():
    assert parse_observable("electron.pt")
    assert parse_observable("jet.constituents.pt")

    with pytest.raises(ValueError):
        parse_observable("unknown")
