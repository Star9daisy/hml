import numpy as np
import pytest

from ..events.delphes_events import DelphesEvents
from .collective import Collective
from .nested import Nested
from .single import Single


@pytest.fixture
def event():
    events = DelphesEvents("tests/data/pp2tt/Events/run_01/tag_1_delphes_events.root")
    yield events[0]


def test_attributes():
    obj = Nested(Single("Jet", 0), Single("Particles", 0))
    assert obj.main == Single("Jet", 0)
    assert obj.sub == Single("Particles", 0)
    assert obj.objects == []
    assert obj.id == "Jet0.Particles0"
    assert repr(obj) == "Nested: Jet0.Particles0"
    assert obj.config == {
        "classname": "Nested",
        "main_config": {
            "classname": "Single",
            "field": "Jet",
            "index": 0,
        },
        "sub_config": {
            "classname": "Single",
            "field": "Particles",
            "index": 0,
        },
    }

    obj = Nested(Collective("Jet", 0, 2), Collective("Particles", 0, 3))
    assert obj.main == Collective("Jet", 0, 2)
    assert obj.sub == Collective("Particles", 0, 3)
    assert obj.objects == []
    assert obj.id == "Jet:2.Particles:3"
    assert repr(obj) == "Nested: Jet:2.Particles:3"
    assert obj.config == {
        "classname": "Nested",
        "main_config": {
            "classname": "Collective",
            "field": "Jet",
            "start": 0,
            "stop": 2,
        },
        "sub_config": {
            "classname": "Collective",
            "field": "Particles",
            "start": 0,
            "stop": 3,
        },
    }


def test_from_identifier():
    assert Nested.from_id("Jet0.Particles0") == Nested(
        Single("Jet", 0), Single("Particles", 0)
    )
    assert Nested.from_id("Jet0.Particles1") != Nested(
        Single("Jet", 0), Single("Particles", 0)
    )

    with pytest.raises(ValueError):
        Nested.from_id("Jet0")

    with pytest.raises(ValueError):
        Nested.from_id("Jet")

    with pytest.raises(ValueError):
        Nested.from_id("Jet0,Jet1")


def test_from_config():
    obj = Nested(Single("Jet", 0), Single("Particles", 0))
    assert obj == Nested.from_config(obj.config)

    obj = Nested(Collective("Jet", 0, 2), Collective("Particles", 0, 3))
    assert obj == Nested.from_config(obj.config)

    with pytest.raises(ValueError):
        Nested.from_config({"classname": "Unknown"})


def test_read(event):
    # (v, v)
    # v != 0
    obj = Nested.from_id("Jet0.Particles0")
    assert np.array(obj.read_ttree(event).objects).shape == (1, 1)

    obj = Nested.from_id("Jet:10.Particles:10")
    assert np.array(obj.read_ttree(event).objects).shape == (10, 10)

    # v == 0
    # (0, v) -> (0,)
    obj = Nested.from_id("Jet100.Particles0")
    assert np.array(obj.read_ttree(event).objects).shape == (0,)

    obj = Nested.from_id("Jet0.Particles100")
    assert np.array(obj.read_ttree(event).objects).shape == (1, 0)

    obj = Nested.from_id("Jet100:.Particles100")
    assert np.array(obj.read_ttree(event).objects).shape == (0,)

    obj = Nested.from_id("Jet:10.Particles100:")
    assert np.array(obj.read_ttree(event).objects).shape == (10, 0)
