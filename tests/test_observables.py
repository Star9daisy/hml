from hml.generators import Madgraph5Run
from hml.observables import *
from hml.types import Path

DATA_DIR = Path("tests/data")
run_tt = Madgraph5Run(DATA_DIR / "pp2tt", "run_01")
run_zz = Madgraph5Run(DATA_DIR / "pp2zz", "run_01")
event_tt = next(iter(run_tt.events()))
event_zz = next(iter(run_zz.events()))


def test_four_vector():
    for obs_cls in [Px, Py, Pz, E, Pt, Eta, Phi, M]:
        obs = obs_cls("Jet0")
        obs.read(event_tt)
        assert obs.shape == "1 * float32"

        obs = obs_cls("Jet:2")
        obs.read(event_tt)
        assert obs.shape == "2 * float32"

        obs = obs_cls("Jet0.Constituents:10")
        obs.read(event_tt)
        assert obs.shape == "1 * 10 * float32"

        obs = obs_cls("Jet:2.Constituents:10")
        obs.read(event_tt)
        assert obs.shape == "2 * 10 * float32"

        obs = obs_cls("Jet:2.Constituents")
        obs.read(event_tt)
        assert obs.shape == "2 * var * float32"

        obs = obs_cls("Jet:200.Constituents:200")
        obs.read(event_tt)
        assert obs.shape == "200 * 200 * float32"

        obs = obs_cls("Jet0,Jet1")
        obs.read(event_tt)
        assert obs.value == None


def test_n_subjettiness():
    obs = NSubjettiness("FatJet0", 1)
    obs.read(event_zz)
    assert obs.shape == "1 * float32"
    assert obs.value[0] == event_zz.FatJet[0].Tau[0]

    obs = NSubjettiness("FatJet", 1)
    obs.read(event_zz)
    assert obs.shape == f"{event_zz.FatJet.GetEntries()} * float32"

    obs = NSubjettiness("FatJet:2", 1)
    obs.read(event_zz)
    assert obs.shape == "2 * float32"

    obs = NSubjettiness("FatJet0,FatJet0", 1)
    obs.read(event_zz)
    assert obs.value == None

    obs = NSubjettiness("FatJet0.Constituents", 1)
    obs.read(event_zz)
    assert obs.value == None


def test_n_subjettiness_ratio():
    obs = NSubjettinessRatio("FatJet0", 2, 1)
    obs.read(event_zz)
    assert obs.shape == "1 * float32"
    assert obs.value[0] == event_zz.FatJet[0].Tau[1] / event_zz.FatJet[0].Tau[0]

    obs = NSubjettinessRatio("FatJet", 2, 1)
    obs.read(event_zz)
    assert obs.shape == f"{event_zz.FatJet.GetEntries()} * float32"

    obs = NSubjettinessRatio("FatJet:2", 2, 1)
    obs.read(event_zz)
    assert obs.shape == "2 * float32"

    obs = NSubjettinessRatio("FatJet0,FatJet0", 2, 1)
    obs.read(event_zz)
    assert obs.value == None

    obs = NSubjettinessRatio("FatJet0.Constituents", 2, 1)
    obs.read(event_zz)
    assert obs.value == None


def test_b_tag():
    obs = BTag("FatJet0")
    obs.read(event_zz)
    assert obs.shape == "1 * float32"
    assert obs.value[0] == event_zz.FatJet[0].BTag

    obs = BTag("FatJet")
    obs.read(event_zz)
    assert obs.shape == f"{event_zz.FatJet.GetEntries()} * float32"

    obs = BTag("FatJet:2")
    obs.read(event_zz)
    assert obs.shape == "2 * float32"

    obs = BTag("FatJet0,FatJet0")
    obs.read(event_zz)
    assert obs.value == None

    obs = BTag("FatJet0.Constituents")
    obs.read(event_zz)
    assert obs.value == None


def test_charge():
    obs = Charge("Jet0")
    obs.read(event_zz)
    assert obs.shape == "1 * float32"
    assert obs.value[0] == event_zz.Jet[0].Charge

    obs = Charge("Jet")
    obs.read(event_zz)
    assert obs.shape == f"{event_zz.Jet.GetEntries()} * float32"

    obs = Charge("Jet:2")
    obs.read(event_zz)
    assert obs.shape == "2 * float32"

    obs = Charge("Jet:2")
    obs.read(event_zz)
    assert obs.shape == "2 * float32"

    obs = Charge("Jet0,Jet0")
    obs.read(event_zz)
    assert obs.value == None

    obs = Charge("Jet0.Constituents")
    obs.read(event_zz)
    assert obs.value == None


def test_size():
    obs = Size("Jet")
    obs.read(event_tt)
    assert obs.shape == "1 * float32"
    assert obs.value[0] == event_tt.Jet.GetEntries()

    obs = Size("Jet:2")
    obs.read(event_tt)
    assert obs.shape == "1 * float32"
    assert obs.value[0] == 2

    obs = Size("Jet,Jet")
    obs.read(event_tt)
    assert obs.value == None

    obs = Size("Jet0")
    obs.read(event_tt)
    assert obs.value == None

    obs = Size("Jet.Constituents")
    obs.read(event_tt)
    assert obs.value == None
