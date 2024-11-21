import pytest

from hml.physics_objects.nested import Constituents, Reclustered
from hml.physics_objects.single import Electron, FatJet, Jet


def test_reclustered_init():
    # ------------------------------------------------------------------------ #
    BRANCH = Jet(algorithm="kt", radius=0.4)
    obj = Reclustered(branch=BRANCH)

    assert obj.branch.algorithm == BRANCH.algorithm
    assert obj.branch.radius == BRANCH.radius
    assert obj.branch.branch == BRANCH.branch
    assert obj.branch.class_name == BRANCH.class_name

    assert obj.class_name == "reclustered"

    # ------------------------------------------------------------------------ #
    with pytest.raises(TypeError):
        Reclustered(branch=Electron())

    # ------------------------------------------------------------------------ #
    with pytest.raises(ValueError):
        Reclustered(branch=Jet())


def test_reclustered_read(events):
    # ------------------------------------------------------------------------ #
    obj = Reclustered(branch=Jet(algorithm="kt", radius=0.4)).read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * var * {")
    assert obj.constituents.fields == ["pt", "eta", "phi", "mass"]
    assert obj.constituents.typestr.startswith("100 * var * var * var * {")


def test_reclustered_from_name():
    # ------------------------------------------------------------------------ #
    obj = Reclustered.from_name("ak8fatjet.reclustered")

    assert obj.branch.algorithm == "ak"
    assert obj.branch.radius == 0.8
    assert obj.branch.branch == "FatJet"
    assert obj.branch.class_name == "fatjet"

    assert obj.class_name == "reclustered"

    # ------------------------------------------------------------------------ #
    obj = Reclustered.from_name("kt4jet.reclustered")

    assert obj.branch.algorithm == "kt"
    assert obj.branch.radius == 0.4
    assert obj.branch.branch == "Jet"
    assert obj.branch.class_name == "jet"

    # ------------------------------------------------------------------------ #
    with pytest.raises(ValueError):
        Reclustered.from_name("electron.reclustered")


def test_constituents_init():
    # ------------------------------------------------------------------------ #
    BRANCH = Jet()
    obj = Constituents(branch=BRANCH)

    assert obj.branch.algorithm == BRANCH.algorithm
    assert obj.branch.radius == BRANCH.radius
    assert obj.branch.branch == BRANCH.branch
    assert obj.branch.class_name == BRANCH.class_name

    assert obj.class_name == "constituents"

    # ------------------------------------------------------------------------ #
    with pytest.raises(TypeError):
        Constituents(branch=Electron())


def test_constituents_read(events):
    # ------------------------------------------------------------------------ #
    obj = Constituents(branch=Jet()).read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * var * {")

    # ------------------------------------------------------------------------ #
    obj = Constituents(branch=Reclustered(branch=Jet(algorithm="kt", radius=0.4)))
    obj.read(events)

    assert obj.array.fields == ["pt", "eta", "phi", "mass"]
    assert obj.array.typestr.startswith("100 * var * var * var * {")


def test_nested_from_name():
    # ------------------------------------------------------------------------ #
    obj = Constituents.from_name("kt4jet.reclustered.constituents")

    assert obj.branch.branch.algorithm == "kt"
    assert obj.branch.branch.radius == 0.4
    assert obj.branch.branch.branch == "Jet"
    assert obj.branch.branch.class_name == "jet"

    assert obj.branch.class_name == "reclustered"

    assert obj.class_name == "constituents"

    # ------------------------------------------------------------------------ #
    obj = Constituents.from_name("ak8fatjet.constituents")

    assert obj.branch.algorithm == "ak"
    assert obj.branch.radius == 0.8
    assert obj.branch.branch == "FatJet"
    assert obj.branch.class_name == "fatjet"

    # ------------------------------------------------------------------------ #
    obj = Constituents.from_name("kt4jet.constituents")

    assert obj.branch.algorithm == "kt"
    assert obj.branch.radius == 0.4

    assert obj.branch.branch == "Jet"
    assert obj.branch.class_name == "jet"

    # ------------------------------------------------------------------------ #
    with pytest.raises(ValueError):
        Constituents.from_name("electron.constituents")
