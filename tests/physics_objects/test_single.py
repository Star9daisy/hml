import pytest

from hml.events import load_events
from hml.physics_objects import Electron, Jet, MissingET, Muon, Photon, Tower, Track
from hml.saving import retrieve


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_electron(events):
    obj = Electron()

    # Special methods -------------------------------------------------------- #
    assert repr(obj) == "electron: not read yet"

    # Properties ------------------------------------------------------------- #
    assert obj.key == "electron"
    assert obj.index == slice(None)
    assert obj.array.typestr == "0 * unknown"
    assert obj.name == "electron"
    assert obj.config == {"key": "electron", "index": "", "name": "electron"}

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert repr(obj) == "electron: 5 observables"
    assert obj.array.typestr.startswith("100 * 0 * {")
    assert obj.array.fields == ["pt", "eta", "phi", "mass", "charge"]

    # Class methods ---------------------------------------------------------- #
    assert Electron.from_config(obj.config).config == obj.config

    # Others ----------------------------------------------------------------- #
    # Check array shape for different indices
    obj = Electron(index=0).read(events)
    assert obj.array.typestr.startswith("100 * ?{")

    obj = Electron(index=slice(10)).read(events)
    assert obj.array.typestr.startswith("100 * 10 * ?{")

    obj = Electron(index=slice(10, None)).read(events)
    assert obj.array.typestr.startswith("100 * 0 * {")

    # Check registered names
    assert retrieve("electron")


def test_directly_retrieved_jet(events):
    obj = Jet()

    # Special methods -------------------------------------------------------- #
    assert repr(obj) == "jet: not read yet"

    # Properties ------------------------------------------------------------- #
    assert obj.key == "jet"
    assert obj.index == slice(None)
    assert obj.array.typestr == "0 * unknown"
    assert obj.name == "jet"
    assert obj.config == {
        "key": "jet",
        "index": "",
        "name": "jet",
        "algorithm": None,
        "radius": None,
    }

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert repr(obj) == "jet: 12 observables"
    assert obj.array.typestr.startswith("100 * var * {")
    assert obj.array.fields == [
        "pt",
        "eta",
        "phi",
        "mass",
        "b_tag",
        "tau_tag",
        "charge",
        "tau1",
        "tau2",
        "tau3",
        "tau4",
        "tau5",
    ]

    # Class methods ---------------------------------------------------------- #
    assert Jet.from_config(obj.config).config == obj.config

    # Others ----------------------------------------------------------------- #
    # Check array shape for different indices
    obj = Jet(index=0).read(events)
    assert obj.array.typestr.startswith("100 * {")

    obj = Jet(index=10).read(events)
    assert obj.array.typestr.startswith("100 * ?{")

    obj = Jet(index=slice(1)).read(events)
    assert obj.array.typestr.startswith("100 * 1 * {")

    obj = Jet(index=slice(10)).read(events)
    assert obj.array.typestr.startswith("100 * 10 * ?")

    obj = Jet(index=slice(1, None)).read(events)
    assert obj.array.typestr.startswith("100 * var * {")

    obj = Jet(index=slice(10, None)).read(events)
    assert obj.array.typestr.startswith("100 * 0 * {")

    obj = Jet(index=slice(0, 10)).read(events)
    assert obj.array.typestr.startswith("100 * 10 * ?")

    # Check registered names
    assert retrieve("jet")
    assert retrieve("fatjet")
    assert retrieve("fat_jet")


def test_clustered_jet(events):
    obj = Jet(algorithm="kt", radius=0.4)

    # Special methods -------------------------------------------------------- #
    assert repr(obj) == "kt4jet: not read yet"

    # Properties ------------------------------------------------------------- #
    assert obj.key == "jet"
    assert obj.index == slice(None)
    assert obj.array.typestr == "0 * unknown"
    assert obj.name == "kt4jet"
    assert obj.config == {
        "key": "jet",
        "index": "",
        "name": "kt4jet",
        "algorithm": "kt",
        "radius": 0.4,
    }

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert repr(obj) == "kt4jet: 4 observables"
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Class methods ---------------------------------------------------------- #
    assert Jet.from_config(obj.config).config == obj.config

    # Others ----------------------------------------------------------------- #
    # Check registered names
    assert retrieve("kt4jet")
    assert retrieve("ca8fat_jet")
    assert retrieve("ak10fatjet")


def test_missing_et(events):
    obj = MissingET()

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Others ----------------------------------------------------------------- #
    # Check registered names
    assert retrieve("missing_et")
    assert retrieve("met")


def test_muon(events):
    obj = Muon()

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert obj.array.fields == ["pt", "eta", "phi", "mass", "charge"]

    # Others ----------------------------------------------------------------- #
    # Check registered names
    assert retrieve("muon")


def test_photon(events):
    obj = Photon()

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Others ----------------------------------------------------------------- #
    # Check registered names
    assert retrieve("photon")


def test_tower(events):
    obj = Tower()

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Others ----------------------------------------------------------------- #
    # Check registered names
    assert retrieve("tower")


def test_track(events):
    obj = Track()

    # Methods ---------------------------------------------------------------- #
    assert obj.read(events)
    assert obj.array.fields == ["pt", "eta", "phi", "mass"]

    # Others ----------------------------------------------------------------- #
    # Check registered names
    assert retrieve("track")
