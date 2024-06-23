import awkward as ak
import pytest
import uproot

from hml.operations import uproot_ops as upo


def test_branch_to_momentum4d():
    tree = uproot.open("tag_1_delphes_events.root")["Delphes"]
    _ = upo.branch_to_momentum4d(tree["Jet"])
    _ = upo.branch_to_momentum4d(tree["Jet.Constituents"])
    _ = upo.branch_to_momentum4d(tree["Electron"])
    _ = upo.branch_to_momentum4d(tree["Muon"])
    _ = upo.branch_to_momentum4d(tree["MissingET"])
    _ = upo.branch_to_momentum4d(tree["Photon"])
    _ = upo.branch_to_momentum4d(tree["Track"])
    _ = upo.branch_to_momentum4d(tree["Tower"])
    _ = upo.branch_to_momentum4d(tree["Particle"])

    # Bad
    with pytest.raises(ValueError):
        upo.branch_to_momentum4d(tree["ScalarHT"])


def test_top_level_branch_to_momentum4d():
    tree = uproot.open("tag_1_delphes_events.root")["Delphes"]

    # Good
    _ = upo.top_level_branch_to_momentum4d(tree["Jet"])

    # Bad
    with pytest.raises(ValueError):
        upo.top_level_branch_to_momentum4d(tree["Jet.Constituents"])


def test_sub_level_branch_to_momentum4d():
    tree = uproot.open("tag_1_delphes_events.root")["Delphes"]

    # Good
    _ = upo.sub_level_branch_to_momentum4d(tree["Jet.Constituents"])

    # Bad
    with pytest.raises(ValueError):
        upo.sub_level_branch_to_momentum4d(tree["Jet"])
    with pytest.raises(ValueError):
        upo.sub_level_branch_to_momentum4d(tree["Jet.Particles"])


def test_retrieve_constituents_from_eflows():
    tree = uproot.open("tag_1_delphes_events.root")["Delphes"]
    constituents = tree["Jet.Constituents"]

    reference_ids = constituents.array()["refs"]
    events = constituents.parent.parent

    tracks = upo.top_level_branch_to_momentum4d(events["EFlowTrack"])
    track_ids = events["EFlowTrack.fUniqueID"].array()

    photons = upo.top_level_branch_to_momentum4d(events["EFlowPhoton"])
    photon_ids = events["EFlowPhoton.fUniqueID"].array()

    hadrons = upo.top_level_branch_to_momentum4d(events["EFlowNeutralHadron"])
    hadron_ids = events["EFlowNeutralHadron.fUniqueID"].array()

    eflows = ak.concatenate([tracks, photons, hadrons], axis=1)
    eflow_ids = ak.concatenate([track_ids, photon_ids, hadron_ids], axis=1)

    reference_ids = reference_ids[:1]
    eflows = eflows[:1]
    eflow_ids = eflow_ids[:1]

    _ = upo.retrieve_constituents_from_eflows.py_func(
        reference_ids, eflow_ids, eflows, ak.ArrayBuilder()
    )
