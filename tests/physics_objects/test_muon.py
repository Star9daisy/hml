import awkward as ak

from hml.events import DelphesEvent
from hml.physics_objects import Muon


class TestMuon:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)

    def test_read(self):
        muons = Muon().read(self.events)

        assert ak.all(self.events["Muon.PT"] == muons.p4.pt)
        assert ak.all(self.events["Muon.Eta"] == muons.p4.eta)
        assert ak.all(self.events["Muon.Phi"] == muons.p4.phi)
        assert ak.all(muons.p4.mass == 0)
        assert ak.all(self.events["Muon.Charge"] == muons.p4.charge)
