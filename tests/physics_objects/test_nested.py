from hml.events import load_events
from hml.physics_objects import Constituents
from hml.saving import retrieve

events = load_events("tag_1_delphes_events.root")


def test_constituents():
    # Check __init__
    csts = Constituents(["jet", "constituents"])

    # Check __repr__
    assert repr(csts) == "jet.constituents -> (not read yet)"

    # Check properties
    assert csts.keys == ["jet", "constituents"]
    assert csts.indices == [slice(None), slice(None)]
    assert csts.array.typestr == "0 * unknown"

    # Check read
    assert csts.read(events)  # Ensure the returned value is not None

    assert repr(csts) == "jet.constituents -> (pt, eta, phi, mass)"
    assert csts.array.typestr[:19] == "100 * var * var * {"
    assert csts.array.fields == ["pt", "eta", "phi", "mass"]

    # Check config
    assert csts.config == {
        "keys": ["jet", "constituents"],
        "indices": ["", ""],
        "class_alias": None,
    }

    # Check from_config
    assert Constituents.from_config(csts.config).config == csts.config

    # Check array typestr
    csts = Constituents(["jet", "constituents"]).read(events)
    assert csts.array.typestr[:19] == "100 * var * var * {"

    csts = Constituents(
        ["jet", "constituents"],
        indices=[slice(10), slice(100)],
    ).read(events)
    assert csts.array.typestr[:19] == "100 * 10 * 100 * ?{"

    csts = Constituents(
        ["jet", "constituents"],
        indices=[0, slice(10)],
    ).read(events)
    assert csts.array.typestr[:12] == "100 * 10 * ?"

    # Check registered names
    assert retrieve("constituents")

    # Other cases
    assert Constituents.from_name("jet.constituents").name == "jet.constituents"
