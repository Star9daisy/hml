import pytest

from hml.events import load_events
from hml.observables.angular_distance import DeltaR
from hml.physics_objects import parse_physics_object


@pytest.fixture
def events(root_events_path):
    return load_events(root_events_path)


def test_delta_r(events):
    # Test array types
    obj1 = parse_physics_object("jet0")
    obj2 = parse_physics_object("jet1")
    obs = DeltaR([obj1, obj2])
    assert obs.name == "jet0,jet1.delta_r"
    assert repr(obs) == "jet0,jet1.delta_r: not read yet"
    assert obs.config == {
        "physics_object": ["jet0", "jet1"],
        "name": "jet0,jet1.delta_r",
    }

    obs.read(events)
    assert repr(obs) == "jet0,jet1.delta_r: 100 * ?float32"
    assert obs.array.typestr == "100 * ?float32"
    assert DeltaR.from_config(obs.config).config == obs.config

    obj1 = parse_physics_object("jet:1")
    obj2 = parse_physics_object("jet:100")
    obs = DeltaR([obj1, obj2]).read(events)
    assert obs.array.typestr == "100 * 1 * 100 * ?float32"

    obj1 = parse_physics_object("jet")
    obj2 = parse_physics_object("jet:100")
    obs = DeltaR([obj1, obj2]).read(events)
    assert obs.array.typestr == "100 * var * 100 * ?float32"

    obj1 = parse_physics_object("jet0.constituents:100")
    obj2 = parse_physics_object("jet0.constituents:100")
    obs = DeltaR([obj1, obj2]).read(events)
    assert obs.array.typestr == "100 * 100 * 100 * ?float32"

    obj1 = parse_physics_object("ak8fatjet0.reclustered0.constituents:100")
    obj2 = parse_physics_object("ak8fatjet0.reclustered0.constituents:100")
    obs = DeltaR([obj1, obj2]).read(events)
    assert obs.array.typestr == "100 * 100 * 100 * ?float32"

    obj1 = parse_physics_object("jet:2.constituents:10")
    obj2 = parse_physics_object("jet:3.constituents:5")
    obs = DeltaR([obj1, obj2]).read(events)
    assert obs.array.typestr == "100 * 20 * 15 * ?float32"

    obj1 = parse_physics_object("jet")
    obj2 = parse_physics_object("jet")
    obs = DeltaR([obj1, obj2]).read(events)
    assert obs.array.typestr == "100 * var * var * float32"
