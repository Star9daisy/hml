import pytest

from hml.events import load_events
from hml.observables.invariant_mass import InvM
from hml.physics_objects import parse_physics_object


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_inv_m(events):
    obj1 = parse_physics_object("jet0").read(events)
    obj2 = parse_physics_object("electron0").read(events)
    obs = InvM([obj1, obj2]).read(events)
    assert obs.array.ndim == 1
    assert obs.array.typestr == "100 * ?float32"

    obj1 = parse_physics_object("jet:2").read(events)
    obj2 = parse_physics_object("electron:2").read(events)
    obs = InvM([obj1, obj2]).read(events)
    assert obs.array.ndim == 2
    assert obs.array.typestr == "100 * 2 * ?float32"

    obj1 = parse_physics_object("jet").read(events)
    obj2 = parse_physics_object("jet").read(events)
    obs = InvM([obj1, obj2]).read(events)
    assert obs.array.ndim == 2
    assert obs.array.typestr == "100 * var * float32"

    # Bad case
    # ndim mismatch
    obj1 = parse_physics_object("jet").read(events)
    obj2 = parse_physics_object("jet.constituents").read(events)
    with pytest.raises(ValueError):
        InvM([obj1, obj2]).read(events)

    # type mismatch
    obj1 = parse_physics_object("jet:2").read(events)
    obj2 = parse_physics_object("electron:3").read(events)
    with pytest.raises(ValueError):
        InvM([obj1, obj2]).read(events)
