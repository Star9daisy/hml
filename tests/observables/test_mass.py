import pytest

from hml.events import load_events
from hml.observables.mass import M
from hml.physics_objects import parse_physics_object


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_m(events):
    obs = M(parse_physics_object("jet")).read(events)
    assert obs.array.typestr == "100 * var * float32"
    assert M.from_config(obs.config).config == obs.config

    obs = M(parse_physics_object("jet.constituents")).read(events)
    assert obs.array.typestr == "100 * var * var * float32"
