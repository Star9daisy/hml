import awkward as ak
import pytest
import uproot
from typeguard import TypeCheckError

from hml.events import DelphesEvent


class TestDelphesEvent:
    def setup_method(self):
        self.filepath = "tests/data/pp2zz/Events/run_01/tag_1_delphes_events.root"
        self.tree = uproot.open(self.filepath)["Delphes"]
        self.events = DelphesEvent(self.tree)

    def test_init(self):
        # Good
        _ = DelphesEvent(self.tree)

        # Bad
        with pytest.raises(TypeCheckError):
            DelphesEvent("path_to_root")

    def test_len(self):
        assert len(self.events) == self.tree.num_entries

    def test_get(self):
        assert isinstance(self.events.get("fatjet"), ak.Array)
        assert self.events.get("unknown") is None

    def test_getitem(self):
        # Good
        assert isinstance(self.events["fatjet"], ak.Array)

        # Bad
        with pytest.raises(KeyError):
            self.events["unknown"]

    def test_tree(self):
        assert self.events.tree == self.tree

    def test_keys(self):
        assert "FatJet" in self.events.keys
        assert "fat_jet" in self.events.keys
        assert "fatjet" in self.events.keys

    def test_keys_dict(self):
        assert self.events.keys_dict["FatJet"] == "FatJet"
        assert self.events.keys_dict["fat_jet"] == "FatJet"
        assert self.events.keys_dict["fatjet"] == "FatJet"

    def test_load(self):
        events = DelphesEvent.load(self.filepath)
        assert len(events) == len(self.events)
