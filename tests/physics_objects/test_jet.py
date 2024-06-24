import awkward as ak
import uproot

from hml.events import DelphesEvent
from hml.physics_objects import Jet


class TestJet:
    def setup_method(self):
        self.filepath = (
            "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
        )
        self.events = DelphesEvent.load(self.filepath)
        self.uproot_events = uproot.open(self.filepath)["Delphes"]

    def test_init(self):
        _ = Jet()
        _ = Jet(algorithm="kt", radius=0.4)
        _ = Jet(key="jet")

    def test_read_with_normal_jet(self):
        jets = Jet().read(self.events)
        _ = Jet(key="FatJet.Constituents").read(self.events)

        assert ak.all(self.events["Jet.PT"] == jets.p4.pt)
        assert ak.all(self.events["Jet.Eta"] == jets.p4.eta)
        assert ak.all(self.events["Jet.Phi"] == jets.p4.phi)
        assert ak.all(self.events["Jet.Mass"] == jets.p4.mass)
        assert ak.all(self.events["Jet.Charge"] == jets.p4.charge)
        assert ak.all(self.events["Jet.BTag"] == jets.p4.b_tag)
        assert ak.all(self.events["Jet.TauTag"] == jets.p4.tau_tag)

        assert Jet().read(self.events).config == Jet().read(self.uproot_events).config

    def test_read_with_reclustered_jet(self):
        jets = Jet(algorithm="ak", radius=1, key="FatJet").read(self.events)
        _ = Jet(algorithm="ak", radius=1, key="FatJet.Constituents").read(self.events)

        assert ak.all(abs(jets.p4.pt - self.events["FatJet.PT"]) < 1e-4)

    def test_name(self):
        jets = Jet()
        assert jets.name == "Jet"
        assert jets.name == Jet.from_name(jets.name).name

        jets = Jet(key="jet", indices=0)
        assert jets.name == "jet0"
        assert jets.name == Jet.from_name(jets.name).name

        jets = Jet(key="jet.constituents", indices=[0, slice(200)])
        assert jets.name == "jet0.constituents:200"
        assert jets.name == Jet.from_name(jets.name).name

        jets = Jet(algorithm="ak", radius=0.8, key="fatjet")
        assert jets.name == "ak8fatjet"
        assert jets.name == Jet.from_name(jets.name).name

        jets = Jet(algorithm="ak", radius=0.8, key="fatjet.constituents")
        assert jets.name == "ak8fatjet.constituents"
        assert jets.name == Jet.from_name(jets.name).name

    def test_config(self):
        jets = Jet()
        assert jets.config == {
            "algorithm": None,
            "radius": None,
            "key": "Jet",
            "indices": [""],
        }
        assert jets.config == Jet.from_config(jets.config).config

        jets = Jet(algorithm="ak", radius=0.8, key="fatjet")
        assert jets.config == {
            "algorithm": "ak",
            "radius": 0.8,
            "key": "fatjet",
            "indices": [""],
        }
        assert jets.config == Jet.from_config(jets.config).config

        jets = Jet(algorithm="ak", radius=0.8, key="fatjet.constituents")
        assert jets.config == {
            "algorithm": "ak",
            "radius": 0.8,
            "key": "fatjet.constituents",
            "indices": ["", ""],
        }
        assert jets.config == Jet.from_config(jets.config).config

    def test_p4(self):
        jets = Jet().read(self.events)

        assert jets.p4.ndim == 2

        jets = Jet(key="Jet.Constituents").read(self.events)

        assert jets.p4.ndim == 3

        jets = Jet(indices=0).read(self.events)

        assert jets.p4.ndim == 1
