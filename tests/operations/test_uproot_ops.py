import pytest
import uproot

from hml.operations.uproot_ops import (
    branch_to_momentum4d,
    sub_level_branch_to_momentum4d,
    top_level_branch_to_momentum4d,
)

tree = uproot.open("tag_1_delphes_events.root")["Delphes"]


def test_top_level_branch_to_momentum4d():
    for branch in [
        "Particle",
        "Track",
        "Tower",
        "EFlowTrack",
        "EFlowPhoton",
        "EFlowNeutralHadron",
        "GenJet",
        "GenMissingET",
        "Jet",
        "Electron",
        "Photon",
        "Muon",
        "FatJet",
        "MissingET",
    ]:
        top_level_branch_to_momentum4d(tree[branch])

        with pytest.raises(ValueError):
            top_level_branch_to_momentum4d(tree["Jet.Constituents"])

        with pytest.raises(ValueError):
            top_level_branch_to_momentum4d(tree["ScalarHT"])


def test_sub_level_branch_to_momentum4d():
    for branch in ["Jet.Constituents", "FatJet.Constituents"]:
        sub_level_branch_to_momentum4d(tree[branch])

    with pytest.raises(ValueError):
        sub_level_branch_to_momentum4d(tree["Jet"])

    with pytest.raises(ValueError):
        sub_level_branch_to_momentum4d(tree["Jet.Particles"])


def test_branch_to_momentum4d():
    branch_to_momentum4d(tree["Jet"])
    branch_to_momentum4d(tree["Jet.Constituents"])
