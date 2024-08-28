import pytest

from hml.events import load_events
from hml.physics_objects import Constituents, Jet
from hml.saving import retrieve

events = load_events("tag_1_delphes_events.root")


def test_constituents():
    # Check __init__
    csts = Constituents("jet")
    # Or
    csts = Constituents(Jet())

    # Check __repr__
    assert repr(csts) == "jet.constituents -> not read yet"

    # Check properties
    assert csts.key == "constituents"
    assert csts.index == slice(None)
    assert csts.array.typestr == "0 * unknown"

    # Check read
    assert csts.read(events)  # Ensure the returned value is not None

    assert repr(csts) == "jet.constituents -> 100 * var * var * {4 observables}"
    assert csts.array.typestr[:19] == "100 * var * var * {"
    assert csts.array.fields == ["pt", "eta", "phi", "mass"]

    # Check config
    assert csts.config == {
        "source": "jet",
        "key": "constituents",
        "index": "",
        "name": None,
    }

    # Check from_config
    assert Constituents.from_config(csts.config).config == csts.config

    # Check array typestr
    csts = Constituents("jet").read(events)
    assert csts.array.typestr[:19] == "100 * var * var * {"

    csts = Constituents("jet:10", index=slice(100)).read(events)
    assert csts.array.typestr[:19] == "100 * 10 * 100 * ?{"

    csts = Constituents("jet0", index=slice(10)).read(events)
    assert csts.array.typestr[:12] == "100 * 10 * ?"

    # Check registered names
    assert retrieve("jet0.constituents")

    # Bad case
    with pytest.raises(ValueError):
        Constituents("unknown")
