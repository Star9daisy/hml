import awkward as ak

from hml.events import DelphesEvent
from hml.physics_objects import Track


class TestTrack:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)

    def test_read(self):
        tracks = Track().read(self.events)

        assert ak.all(self.events["Track.PT"] == tracks.p4.pt)
        assert ak.all(self.events["Track.Eta"] == tracks.p4.eta)
        assert ak.all(self.events["Track.Phi"] == tracks.p4.phi)
        assert ak.all(self.events["Track.Mass"] == tracks.p4.mass)
