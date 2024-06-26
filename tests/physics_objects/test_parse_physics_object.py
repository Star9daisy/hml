from hml.physics_objects import Jet, parse_physics_object
from hml.registration import init_registry, register


def test_built_in():
    assert parse_physics_object("jet").config == Jet(key="jet").config
    assert (
        parse_physics_object("jet.constituents").config
        == Jet(key="jet.constituents").config
    )
    assert parse_physics_object("jet10").config == Jet(key="jet", indices=10).config
    assert (
        parse_physics_object("jet:10.constituents:20").config
        == Jet(key="jet.constituents", indices=[slice(10), slice(20)]).config
    )

    init_registry()
    subjets = Jet(algorithm="ak", radius=0.8, key="fatjet")
    register(subjets, "subjets")
    parse_physics_object("subjets")
