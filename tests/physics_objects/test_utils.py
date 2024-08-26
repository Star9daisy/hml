from hml.physics_objects import parse_physics_object


def test_parse_physics_object():
    assert parse_physics_object("electron")
    assert parse_physics_object("constituents")
