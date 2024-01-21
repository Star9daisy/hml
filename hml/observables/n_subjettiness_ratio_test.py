from math import isnan

import pytest

from ..events.delphes_events import DelphesEvents
from .n_subjettiness_ratio import NSubjettinessRatio
from .n_subjettiness_ratio import TauMN


@pytest.fixture
def event():
    events = DelphesEvents("tests/data/pp2zz/Events/run_01/tag_1_delphes_events.root")
    yield events[0]


def test_n_subjettiness(event):
    obs = NSubjettinessRatio(m=2, n=1, physics_object="FatJet0")
    assert obs.m == 2
    assert obs.n == 1
    assert obs.physics_object.name == "FatJet0"
    assert obs.supported_objects == ["single", "collective"]
    assert obs.name == "NSubjettinessRatio"
    assert isnan(obs.value)
    assert obs.fullname == "FatJet0.NSubjettinessRatio"
    assert repr(obs) == f"{obs.fullname}: {obs.value}"
    assert obs.classname == "NSubjettinessRatio"
    assert obs.config == {
        "m": 2,
        "n": 1,
        "physics_object": "FatJet0",
        "name": None,
        "value": None,
        "supported_objects": ["single", "collective"],
    }
    assert (
        NSubjettinessRatio.from_name("FatJet0.NSubjettinessRatio", 2, 1).fullname
        == obs.fullname
    )
    assert NSubjettinessRatio.from_config(obs.config).fullname == obs.fullname

    obs.read(event)
    assert isinstance(obs.value, float)

    obs = NSubjettinessRatio(m=2, n=1, physics_object="FatJet:5")
    assert obs.m == 2
    assert obs.n == 1
    assert obs.physics_object.name == "FatJet:5"
    assert obs.supported_objects == ["single", "collective"]
    assert obs.name == "NSubjettinessRatio"
    assert isnan(obs.value)
    assert obs.fullname == "FatJet:5.NSubjettinessRatio"
    assert repr(obs) == f"{obs.fullname}: {obs.value}"
    assert obs.classname == "NSubjettinessRatio"
    assert obs.physics_object.name == "FatJet:5"
    assert obs.config == {
        "m": 2,
        "n": 1,
        "physics_object": "FatJet:5",
        "name": None,
        "value": None,
        "supported_objects": ["single", "collective"],
    }
    assert (
        NSubjettinessRatio.from_name("FatJet:5.NSubjettinessRatio", 2, 1).fullname
        == obs.fullname
    )
    assert NSubjettinessRatio.from_config(obs.config).fullname == obs.fullname

    obs.read(event)
    assert len(obs.value) == 5


def test_tau_m_n(event):
    obs = TauMN(m=2, n=1, physics_object="FatJet0")
    assert obs.m == 2
    assert obs.n == 1
    assert obs.physics_object.name == "FatJet0"
    assert obs.supported_objects == ["single", "collective"]
    assert obs.name == "Tau21"
    assert isnan(obs.value)
    assert obs.fullname == "FatJet0.Tau21"
    assert repr(obs) == f"{obs.fullname}: {obs.value}"
    assert obs.classname == "TauMN"
    assert obs.config == {
        "m": 2,
        "n": 1,
        "physics_object": "FatJet0",
        "name": None,
        "value": None,
        "supported_objects": ["single", "collective"],
    }
    assert TauMN.from_name("FatJet0.Tau21").fullname == obs.fullname
    assert TauMN.from_config(obs.config).fullname == obs.fullname

    obs.read(event)
    assert isinstance(obs.value, float)

    obs = TauMN(m=2, n=1, physics_object="FatJet:5")
    assert obs.m == 2
    assert obs.n == 1
    assert obs.physics_object.name == "FatJet:5"
    assert obs.supported_objects == ["single", "collective"]
    assert obs.name == "Tau21"
    assert isnan(obs.value)
    assert obs.fullname == "FatJet:5.Tau21"
    assert repr(obs) == f"{obs.fullname}: {obs.value}"
    assert obs.classname == "TauMN"
    assert obs.config == {
        "m": 2,
        "n": 1,
        "physics_object": "FatJet:5",
        "name": None,
        "value": None,
        "supported_objects": ["single", "collective"],
    }
    assert TauMN.from_name("FatJet:5.Tau21").fullname == obs.fullname
    assert TauMN.from_config(obs.config).fullname == obs.fullname

    obs.read(event)
    assert len(obs.value) == 5


def test_bad_physics_object(event):
    assert isnan(TauMN(m=2, n=1, physics_object="Jet100").read(event).value)

    with pytest.raises(TypeError):
        TauMN.from_name("Tau21")
