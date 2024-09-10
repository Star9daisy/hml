import pytest

from hml.events import load_events
from hml.physics_objects import Constituents, Electron, Jet, Reclustered
from hml.saving import retrieve


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_constituents(events):
    obj = Constituents(Jet())
    # Bad case
    with pytest.raises(ValueError):
        Constituents(Electron())

    # Special methods -------------------------------------------------------- #
    assert repr(obj) == "jet.constituents: not read yet"

    # Properties ------------------------------------------------------------- #
    assert obj.source.name == "jet"
    assert obj.key == "constituents"
    assert obj.index == slice(None)
    assert obj.array.typestr == "0 * unknown"
    assert obj.name == "jet.constituents"
    assert obj.config == {
        "source": "jet",
        "key": "constituents",
        "index": "",
        "name": "jet.constituents",
    }

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert repr(obj) == "jet.constituents: 4 observables"
    assert obj.array.typestr.startswith("100 * var * var * {")
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Class methods ---------------------------------------------------------- #
    assert Constituents.from_config(obj.config).config == obj.config
    # Bad case
    with pytest.raises(ValueError):
        Constituents.from_config({"source": "unknown"})

    # Others ----------------------------------------------------------------- #
    # Check array shape for different indices
    source = Reclustered(Jet(algorithm="ak", radius=1.0))
    obj = Constituents(source).read(events)
    assert obj.array.typestr.startswith("100 * var * var * var * {")

    source = Reclustered(Jet(algorithm="ak", radius=1.0, index=0))
    obj = Constituents(source).read(events)
    assert obj.array.typestr.startswith("100 * var * var * {")

    source = Reclustered(Jet(algorithm="ak", radius=1.0, index=0), index=0)
    obj = Constituents(source).read(events)
    assert obj.array.typestr.startswith("100 * var * {")

    source = Reclustered(Jet(algorithm="ak", radius=1.0, index=0), index=0)
    obj = Constituents(source, index=0).read(events)
    assert obj.array.typestr.startswith("100 * {")

    # Check registered names
    assert retrieve("jet.constituents")
    assert retrieve("ak10jet.constituents")
    assert retrieve("ak10jet.reclustered.constituents")


def test_reclustered(events):
    obj = Reclustered(Jet(algorithm="ak", radius=1.0))
    # Bad case
    with pytest.raises(ValueError):
        Reclustered(Electron())
    with pytest.raises(ValueError):
        Reclustered(Jet())

    # Special methods -------------------------------------------------------- #
    assert repr(obj) == "ak10jet.reclustered: not read yet"

    # Properties ------------------------------------------------------------- #
    assert obj.source.name == "ak10jet"
    assert obj.key == "reclustered"
    assert obj.index == slice(None)
    assert obj.array.typestr == "0 * unknown"
    assert obj.name == "ak10jet.reclustered"
    assert obj.config == {
        "source": "ak10jet",
        "key": "reclustered",
        "index": "",
        "name": "ak10jet.reclustered",
    }

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert repr(obj) == "ak10jet.reclustered: 4 observables"
    assert obj.array.typestr.startswith("100 * var * var * {")
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Class methods ---------------------------------------------------------- #
    assert Reclustered.from_config(obj.config).config == obj.config
    # Bad case
    with pytest.raises(ValueError):
        Reclustered.from_config({"source": "unknown"})

    # Others ----------------------------------------------------------------- #
    # Check array shape for different indices
    source = Jet(algorithm="ak", radius=1.0)

    obj = Reclustered(source, index=0).read(events)
    assert obj.array.typestr.startswith("100 * var * {")

    obj = Reclustered(source, index=slice(1)).read(events)
    assert obj.array.typestr.startswith("100 * var * 1 * {")

    obj = Reclustered(source, index=slice(10)).read(events)
    assert obj.array.typestr.startswith("100 * var * 10 * ?{")

    obj = Reclustered(source, index=slice(1, None)).read(events)
    assert obj.array.typestr.startswith("100 * var * var * {")

    obj = Reclustered(source, index=slice(100, None)).read(events)
    assert obj.array.typestr.startswith("100 * var * var * {")

    source = Jet(algorithm="ak", radius=1.0, index=0)
    obj = Reclustered(source, index=slice(100, None)).read(events)
    assert obj.array.typestr.startswith("100 * var * {")

    source = Jet(algorithm="ak", radius=1.0, index=slice(100, None))
    obj = Reclustered(source, index=slice(100, None)).read(events)
    assert obj.array.typestr.startswith("100 * var * var * {")

    # Check registered names
    assert retrieve("ak10jet.reclustered")
