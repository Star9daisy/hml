import pytest

from hml.events import load_events
from hml.observables.tag import BTag, TauTag
from hml.physics_objects import parse_physics_object


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_btag(events):
    obs = BTag(parse_physics_object("jet")).read(events)
    assert obs.array.typestr == "100 * var * uint32"


def test_tautag(events):
    obs = TauTag(parse_physics_object("jet")).read(events)
    assert obs.array.typestr == "100 * var * uint32"
