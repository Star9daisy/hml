import awkward as ak

from hml.events import DelphesEvent
from hml.physics_objects import Photon


class TestPhoton:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)

    def test_read(self):
        photons = Photon().read(self.events)

        assert ak.all(self.events["Photon.PT"] == photons.p4.pt)
        assert ak.all(self.events["Photon.Eta"] == photons.p4.eta)
        assert ak.all(self.events["Photon.Phi"] == photons.p4.phi)
        assert ak.all(photons.p4.mass == 0)
