import awkward as ak
import pytest
import uproot

from hml.events import ROOTEvents


def test_root_events():
    # Init
    tree = uproot.open("tag_1_delphes_events.root")["Delphes"]
    events = ROOTEvents(tree)

    # Check __len__
    assert len(events) == 100

    # Check __getitem__
    # Good
    assert ak.all(events["fat_jet.pt"] == events.tree["FatJet.PT"].array())
    # Bad
    with pytest.raises(KeyError):
        events["unknown_key"]

    # Check load
    # Good
    assert ROOTEvents.load("tag_1_delphes_events.root")
    # Bad
    with pytest.raises(ValueError):
        ROOTEvents.load("tag_1_delphes_events.root.txt")
