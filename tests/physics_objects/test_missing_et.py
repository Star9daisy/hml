import awkward as ak

from hml.events import DelphesEvent
from hml.physics_objects import MissingET


class TestMissingET:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)

    def test_read(self):
        met = MissingET().read(self.events)

        assert ak.all(self.events["MissingET.MET"] == met.p4.pt)
        assert ak.all(self.events["MissingET.Eta"] == met.p4.eta)
        assert ak.all(self.events["MissingET.Phi"] == met.p4.phi)
        assert ak.all(met.p4.mass == 0)

    def test_from_name(self):
        _ = MissingET.from_name("MissingET")
        _ = MissingET.from_name("missinget")
        _ = MissingET.from_name("missing_et")
        _ = MissingET.from_name("MET")
        _ = MissingET.from_name("met")
