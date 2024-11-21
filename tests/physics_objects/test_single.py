from hml.physics_objects.single import (
    Electron,
    FatJet,
    Jet,
    MissingET,
    Muon,
    Photon,
    Tower,
    Track,
)


def test_electron_init():
    # ------------------------------------------------------------------------ #
    obj = Electron()

    assert obj.branch == "Electron"
    assert obj.class_name == "electron"


def test_electron_read(events):
    # ------------------------------------------------------------------------ #
    obj = Electron().read(events)

    assert obj.MASS == 0.51099895
    assert obj.array.fields == ["pt", "eta", "phi", "mass", "charge"]
    assert obj.array.typestr.startswith("100 * var * {")


def test_jet_init():
    # ------------------------------------------------------------------------ #
    obj = Jet()

    assert obj.branch == "Jet"
    assert obj.class_name == "jet"
    assert obj.algorithm is None
    assert obj.radius is None


def test_jet_read(events):
    # ------------------------------------------------------------------------ #
    obj = Jet().read(events)

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
    assert obj.array.typestr.startswith("100 * var * {")

    # ------------------------------------------------------------------------ #
    obj = Jet(algorithm="kt", radius=0.4).read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * {")
    assert obj.constituents.fields == ["pt", "eta", "phi", "mass"]
    assert obj.constituents.typestr.startswith("100 * var * var * {")


def test_jet_name():
    # ------------------------------------------------------------------------ #
    obj = Jet()
    assert obj.name == "jet"

    # ------------------------------------------------------------------------ #
    obj = Jet(algorithm="kt", radius=0.4)
    assert obj.name == "kt4jet"


def test_jet_from_name():
    # ------------------------------------------------------------------------ #
    obj = Jet.from_name("jet")

    assert obj.algorithm is None
    assert obj.radius is None
    assert obj.branch == "Jet"
    assert obj.class_name == "jet"

    # ------------------------------------------------------------------------ #
    obj = Jet.from_name("kt4jet")

    assert obj.algorithm == "kt"
    assert obj.radius == 0.4
    assert obj.branch == "Jet"
    assert obj.class_name == "jet"


def test_jet_config():
    # ------------------------------------------------------------------------ #
    obj = Jet()
    assert obj.config == {
        "algorithm": None,
        "radius": None,
        "branch": "Jet",
        "class_name": "jet",
    }

    # ------------------------------------------------------------------------ #
    obj = Jet(algorithm="kt", radius=0.4)
    assert obj.config == {
        "algorithm": "kt",
        "radius": 0.4,
        "branch": "Jet",
        "class_name": "jet",
    }


def test_jet_from_config():
    # ------------------------------------------------------------------------ #
    CONFIG = {
        "algorithm": None,
        "radius": None,
        "branch": "Jet",
        "class_name": "jet",
    }
    obj = Jet.from_config(CONFIG)

    assert obj.algorithm == CONFIG["algorithm"]
    assert obj.radius == CONFIG["radius"]
    assert obj.branch == CONFIG["branch"]
    assert obj.class_name == CONFIG["class_name"]

    # ------------------------------------------------------------------------ #
    CONFIG = {
        "algorithm": "kt",
        "radius": 0.4,
        "branch": "Jet",
        "class_name": "jet",
    }
    obj = Jet.from_config(CONFIG)

    assert obj.algorithm == CONFIG["algorithm"]
    assert obj.radius == CONFIG["radius"]
    assert obj.branch == CONFIG["branch"]
    assert obj.class_name == CONFIG["class_name"]


def test_fatjet_init():
    # ------------------------------------------------------------------------ #
    obj = FatJet()

    assert obj.algorithm is None
    assert obj.radius is None
    assert obj.branch == "FatJet"
    assert obj.class_name == "fatjet"


def test_fatjet_from_name():
    # ------------------------------------------------------------------------ #
    obj = FatJet.from_name("fatjet")

    assert obj.algorithm is None
    assert obj.radius is None
    assert obj.branch == "FatJet"
    assert obj.class_name == "fatjet"

    # ------------------------------------------------------------------------ #
    obj = FatJet.from_name("ak8fatjet")

    assert obj.algorithm == "ak"
    assert obj.radius == 0.8
    assert obj.branch == "FatJet"
    assert obj.class_name == "fatjet"


def test_missing_et_init():
    # ------------------------------------------------------------------------ #
    obj = MissingET()

    assert obj.branch == "MissingET"
    assert obj.class_name == "met"


def test_missing_et_read(events):
    # ------------------------------------------------------------------------ #
    obj = MissingET().read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * {")


def test_muon_init():
    # ------------------------------------------------------------------------ #
    obj = Muon()

    assert obj.branch == "Muon"
    assert obj.class_name == "muon"


def test_muon_read(events):
    # ------------------------------------------------------------------------ #
    obj = Muon().read(events)

    assert obj.MASS == 105.6583755
    assert obj.array.fields == ["pt", "eta", "phi", "mass", "charge"]
    assert obj.array.typestr.startswith("100 * var * {")


def test_photon_init():
    # ------------------------------------------------------------------------ #
    obj = Photon()

    assert obj.branch == "Photon"
    assert obj.class_name == "photon"


def test_photon_read(events):
    # ------------------------------------------------------------------------ #
    obj = Photon().read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * {")


def test_tower_init():
    # ------------------------------------------------------------------------ #
    obj = Tower()

    assert obj.branch == "Tower"
    assert obj.class_name == "tower"


def test_tower_read(events):
    # ------------------------------------------------------------------------ #
    obj = Tower().read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * {")


def test_track_init():
    # ------------------------------------------------------------------------ #
    obj = Track()

    assert obj.branch == "Track"
    assert obj.class_name == "track"


def test_track_read(events):
    # ------------------------------------------------------------------------ #
    obj = Track().read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * {")
