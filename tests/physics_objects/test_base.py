import pytest

from hml.physics_objects.base import (
    NestedPhysicsObject,
    PhysicsObject,
    SinglePhysicsObject,
)


def test_physics_object_init():
    # ------------------------------------------------------------------------ #
    BRANCH = "PhysicsObject"
    CLASS_NAME = "physics_object"
    obj = PhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj.branch == BRANCH
    assert obj.class_name == CLASS_NAME
    assert obj.array.to_list() == []

    # ------------------------------------------------------------------------ #
    PARENT = PhysicsObject(branch="parent", class_name="Parent")
    CLASS_NAME = "child"
    child = PhysicsObject(branch=PARENT, class_name=CLASS_NAME)

    assert child.branch.branch == PARENT.branch
    assert child.branch.class_name == PARENT.class_name
    assert child.branch.array.to_list() == []

    assert child.class_name == CLASS_NAME
    assert child.array.to_list() == []


def test_physics_object_eq():
    # ------------------------------------------------------------------------ #
    BRANCH = "branch"
    CLASS_NAME = "class_name"
    obj1 = PhysicsObject(branch=BRANCH, class_name=CLASS_NAME)
    obj2 = PhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj1 == obj2

    # ------------------------------------------------------------------------ #
    BRANCH = PhysicsObject(branch="parent", class_name="Parent")
    CLASS_NAME = "class_name"
    obj1 = PhysicsObject(branch=BRANCH, class_name=CLASS_NAME)
    obj2 = PhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj1 == obj2


def test_physics_object_repr():
    # ------------------------------------------------------------------------ #
    obj = PhysicsObject(branch="PhysicsObject", class_name="physics_object")

    with pytest.raises(NotImplementedError):
        repr(obj)


def test_physics_object_read(events):
    # ------------------------------------------------------------------------ #
    obj = PhysicsObject(branch="PhysicsObject", class_name="physics_object")

    with pytest.raises(NotImplementedError):
        obj.read(events)


def test_physics_object_property_name():
    # ------------------------------------------------------------------------ #
    obj = PhysicsObject(branch="PhysicsObject", class_name="physics_object")

    with pytest.raises(NotImplementedError):
        obj.name


def test_physics_object_classmethod_from_name():
    # ------------------------------------------------------------------------ #
    with pytest.raises(NotImplementedError):
        PhysicsObject.from_name(name="physics_object")


def test_physics_object_property_config():
    # ------------------------------------------------------------------------ #
    BRANCH = "PhysicsObject"
    CLASS_NAME = "physics_object"
    obj = PhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj.config == {"branch": BRANCH, "class_name": CLASS_NAME}


def test_physics_object_classmethod_from_config():
    # ------------------------------------------------------------------------ #
    CONFIG = {"branch": "PhysicsObject", "class_name": "physics_object"}
    obj = PhysicsObject.from_config(config=CONFIG)

    assert obj.branch == CONFIG["branch"]
    assert obj.class_name == CONFIG["class_name"]
    assert obj.array.to_list() == []


def test_single_physics_object_init():
    # ------------------------------------------------------------------------ #
    BRANCH = "SinglePhysicsObject"
    CLASS_NAME = "single_physics_object"
    obj = SinglePhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj.branch == BRANCH
    assert obj.class_name == CLASS_NAME
    assert obj.array.to_list() == []


def test_single_physics_object_name():
    # ------------------------------------------------------------------------ #
    BRANCH = "SinglePhysicsObject"
    CLASS_NAME = "single_physics_object"
    obj = SinglePhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj.name == CLASS_NAME


def test_single_physics_object_from_name():
    # ------------------------------------------------------------------------ #
    NAME = "single_physics_object"
    obj = SinglePhysicsObject.from_name(name=NAME)

    assert obj.branch == "SinglePhysicsObject"
    assert obj.class_name == NAME
    assert obj.array.to_list() == []


def test_nested_physics_object_init():
    # ------------------------------------------------------------------------ #
    BRANCH = SinglePhysicsObject(branch="Parent", class_name="parent")
    CLASS_NAME = "child"
    obj = NestedPhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj.branch.branch == BRANCH.branch
    assert obj.branch.class_name == BRANCH.class_name
    assert obj.branch.array.to_list() == []

    assert obj.class_name == CLASS_NAME
    assert obj.array.to_list() == []

    # ------------------------------------------------------------------------ #
    BRANCH1 = SinglePhysicsObject(branch="Parent", class_name="parent")
    BRANCH2 = NestedPhysicsObject(branch=BRANCH1, class_name="child")
    obj = NestedPhysicsObject(branch=BRANCH2, class_name="grandchild")

    assert obj.branch.branch.branch == BRANCH1.branch
    assert obj.branch.branch.class_name == BRANCH1.class_name
    assert obj.branch.branch.array.to_list() == []

    assert obj.branch.class_name == "child"
    assert obj.branch.array.to_list() == []

    assert obj.class_name == "grandchild"
    assert obj.array.to_list() == []


def test_nested_physics_object_name():
    # ------------------------------------------------------------------------ #
    BRANCH = SinglePhysicsObject(branch="Parent", class_name="parent")
    CLASS_NAME = "child"
    obj = NestedPhysicsObject(branch=BRANCH, class_name=CLASS_NAME)

    assert obj.name == "parent.child"

    # ------------------------------------------------------------------------ #
    BRANCH1 = SinglePhysicsObject(branch="Parent", class_name="parent")
    BRANCH2 = NestedPhysicsObject(branch=BRANCH1, class_name="child")
    obj = NestedPhysicsObject(branch=BRANCH2, class_name="grandchild")

    assert obj.name == "parent.child.grandchild"


def test_nested_physics_object_from_name():
    with pytest.raises(NotImplementedError):
        NestedPhysicsObject.from_name(name="parent.child.grandchild")
