import awkward as ak

from hml.events import DelphesEvent
from hml.physics_objects import Tower


class TestTower:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)

    def test_read(self):
        towers = Tower().read(self.events)

        assert ak.all(self.events["Tower.ET"] == towers.p4.pt)
        assert ak.all(self.events["Tower.Eta"] == towers.p4.eta)
        assert ak.all(self.events["Tower.Phi"] == towers.p4.phi)
        assert ak.all(towers.p4.mass == 0)
