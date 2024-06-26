import awkward as ak

from hml.events import DelphesEvent
from hml.physics_objects import Electron


class TestElectron:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)

    def test_read(self):
        electrons = Electron().read(self.events)

        assert ak.all(self.events["Electron.PT"] == electrons.p4.pt)
        assert ak.all(self.events["Electron.Eta"] == electrons.p4.eta)
        assert ak.all(self.events["Electron.Phi"] == electrons.p4.phi)
        assert ak.all(electrons.p4.mass == 0)

    def test_name(self):
        electrons = Electron()
        assert electrons.name == "Electron"
        assert electrons.name == Electron.from_name(electrons.name).name

        electrons = Electron(key="electron", indices=0)
        assert electrons.name == "electron0"
        assert electrons.name == Electron.from_name(electrons.name).name
