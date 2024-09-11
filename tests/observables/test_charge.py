import pytest

from hml.events import load_events
from hml.observables.charge import Charge
from hml.physics_objects import parse_physics_object


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_charge(events):
    obs = Charge(parse_physics_object("jet")).read(events)
    assert obs.array.typestr == "100 * var * int32"
