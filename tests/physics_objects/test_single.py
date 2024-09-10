from hml.events import load_events
from hml.physics_objects import Electron, Jet, MissingET, Muon, Photon, Tower, Track
from hml.saving import retrieve


def test_electron(root_events_path):
    events = load_events(root_events_path)

    # Check __init__
    e = Electron()

    # Check __repr__
    assert repr(e) == "electron -> not read yet"

    # Check properties
    assert e.key == "electron"
    assert e.index == slice(None)
    assert e.array.typestr == "0 * unknown"

    # Check read
    assert e.read(events)  # Ensure the returned value is not None

    assert repr(e) == "electron -> 100 * 0 * {5 observables}"
    assert e.array.fields == ["pt", "eta", "phi", "mass", "charge"]

    # Check config
    assert e.config == {
        "key": "electron",
        "index": "",
        "name": "electron",
    }

    # Check from_config
    assert Electron.from_config(e.config).config == e.config

    # Check array typestr
    e = Electron(index=0).read(events)
    assert e.array.typestr[:7] == "100 * ?"

    e = Electron(index=slice(10)).read(events)
    assert e.array.typestr[:12] == "100 * 10 * ?"

    e = Electron(index=slice(10, None)).read(events)
    assert e.array.typestr[:7] == "100 * 0"

    # Check registered names
    assert retrieve("electron")


def test_jet(root_events_path):
    events = load_events(root_events_path)

    # Check __init__
    jet = Jet()

    # Check __repr__
    assert repr(jet) == "jet -> not read yet"

    # Check properties
    assert jet.key == "jet"
    assert jet.index == slice(None)
    assert jet.array.typestr == "0 * unknown"

    # Check read
    assert jet.read(events)  # Ensure the returned value is not None

    assert repr(jet) == "jet -> 100 * var * {12 observables}"
    assert jet.array.typestr[:9] == "100 * var"
    assert jet.array.fields == [
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

    # Check config
    assert jet.config == {
        "algorithm": None,
        "radius": None,
        "key": "jet",
        "index": "",
        "name": "jet",
    }

    # Check from_config
    assert Jet.from_config(jet.config).config == jet.config

    # Check array typestr
    jet = Jet(index=0).read(events)
    assert jet.array.typestr[:7] == "100 * {"

    jet = Jet(index=10).read(events)
    assert jet.array.typestr[:7] == "100 * ?"

    jet = Jet(index=slice(1)).read(events)
    assert jet.array.typestr[:11] == "100 * 1 * {"

    jet = Jet(index=slice(10)).read(events)
    assert jet.array.typestr[:12] == "100 * 10 * ?"

    jet = Jet(index=slice(1, None)).read(events)
    assert jet.array.typestr[:13] == "100 * var * {"

    jet = Jet(index=slice(10, None)).read(events)
    assert jet.array.typestr[:11] == "100 * 0 * {"

    jet = Jet(index=slice(0, 10)).read(events)
    assert jet.array.typestr[:12] == "100 * 10 * ?"

    # Check registered names
    assert retrieve("jet")
    assert retrieve("fat_jet")


def test_missing_et(root_events_path):
    events = load_events(root_events_path)

    missing_et = MissingET().read(events)

    assert missing_et.array.fields == ["pt", "eta", "phi", "mass"]
    assert retrieve("missing_et")
    assert retrieve("met")


def test_muon(root_events_path):
    events = load_events(root_events_path)

    muon = Muon().read(events)

    assert muon.array.fields == ["pt", "eta", "phi", "mass", "charge"]
    assert retrieve("muon")


def test_photon(root_events_path):
    events = load_events(root_events_path)

    photon = Photon().read(events)

    assert photon.array.fields == ["pt", "eta", "phi", "mass"]
    assert retrieve("photon")


def test_tower(root_events_path):
    events = load_events(root_events_path)

    tower = Tower().read(events)

    assert tower.array.fields == ["pt", "eta", "phi", "mass"]
    assert retrieve("tower")


def test_track(root_events_path):
    events = load_events(root_events_path)

    track = Track().read(events)

    assert track.array.fields == ["pt", "eta", "phi", "mass"]
    assert retrieve("track")
