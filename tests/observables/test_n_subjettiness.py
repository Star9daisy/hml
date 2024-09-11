import pytest

from hml.events import load_events
from hml.observables.n_subjettiness import TauMN, TauN
from hml.physics_objects import parse_physics_object


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_tau_n(events):
    obs = TauN(1, parse_physics_object("fatjet")).read(events)
    assert obs.array.typestr == "100 * var * float32"
    assert obs.config == {"n": 1, "physics_object": "fatjet", "name": "tau1"}
    assert TauN.from_config(obs.config).config == obs.config


def test_tau_mn(events):
    obs = TauMN(2, 1, parse_physics_object("fatjet")).read(events)
    assert obs.array.typestr == "100 * var * float32"
    assert obs.config == {"m": 2, "n": 1, "physics_object": "fatjet", "name": "tau21"}
    assert TauMN.from_config(obs.config).config == obs.config
