import pytest

from hml.operations.uproot import get_branch, get_sub_branch, get_top_branch


def test_get_top_branch(events):
    array = get_top_branch(events, "Particle")
    assert array.typestr.startswith("100 * var * {")

    array = get_top_branch(events, "Particle", as_momentum=True)
    assert array.typestr.startswith("100 * var * Momentum4D")

    _ = get_top_branch(events, "Track")
    _ = get_top_branch(events, "Tower")
    _ = get_top_branch(events, "Jet")
    _ = get_top_branch(events, "Electron")
    _ = get_top_branch(events, "Photon")
    _ = get_top_branch(events, "Muon")
    _ = get_top_branch(events, "MissingET")

    with pytest.raises(ValueError):
        get_top_branch(events, "Jet.Constituents")

    with pytest.raises(ValueError):
        get_top_branch(events, "ScalarHT")


def test_get_sub_branch(events):
    array = get_sub_branch(events, "Jet.Constituents")
    assert array.typestr.startswith("100 * var * var * {")

    array = get_sub_branch(events, "Jet.Constituents", as_momentum=True)
    assert array.typestr.startswith("100 * var * var * Momentum4D")

    with pytest.raises(ValueError):
        get_sub_branch(events, "Jet")

    with pytest.raises(ValueError):
        get_sub_branch(events, "Jet.Particles")


def test_get_branch(events):
    array = get_branch(events, "Jet")
    assert array.typestr.startswith("100 * var * {")

    array = get_branch(events, "Jet", as_momentum=True)
    assert array.typestr.startswith("100 * var * Momentum4D")

    array = get_branch(events, "Jet.Constituents")
    assert array.typestr.startswith("100 * var * var * {")

    array = get_branch(events, "Jet.Constituents", as_momentum=True)
    assert array.typestr.startswith("100 * var * var * Momentum4D")
