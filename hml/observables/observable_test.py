from math import isnan

import pytest

from hml.observables import Observable


def test_observable():
    obs = Observable()
    assert obs.physics_object is None
    assert obs.support_objects == ["all"]
    assert obs.name == "Observable"
    assert isnan(obs.value)
    assert obs.fullname == "Observable"
    assert obs.fullname == repr(obs)
    assert obs.classname == "Observable"
    assert obs.physics_object is None
    assert obs.config == {
        "physics_object": None,
        "name": None,
        "value": None,
        "support_objects": "all",
    }
    assert Observable.from_name("Observable").fullname == obs.fullname
    assert Observable.from_config(obs.config).fullname == obs.fullname

    obs = Observable(physics_object="Jet")
    assert obs.physics_object.name == "Jet"
    assert obs.support_objects == ["all"]
    assert obs.name == "Observable"
    assert isnan(obs.value)
    assert obs.fullname == "Jet.Observable"
    assert obs.fullname == repr(obs)
    assert obs.classname == "Observable"
    assert obs.physics_object.name == "Jet"
    assert obs.config == {
        "physics_object": "Jet",
        "name": None,
        "value": None,
        "support_objects": "all",
    }
    assert Observable.from_name("Jet.Observable").fullname == obs.fullname
    assert Observable.from_config(obs.config).fullname == obs.fullname

    obs = Observable(physics_object="Jet", name="MyObservable")
    assert obs.physics_object.name == "Jet"
    assert obs.support_objects == ["all"]
    assert obs.name == "MyObservable"
    assert isnan(obs.value)
    assert obs.fullname == "Jet.MyObservable"
    assert obs.fullname == repr(obs)
    assert obs.classname == "Observable"
    assert obs.physics_object.name == "Jet"
    assert obs.config == {
        "physics_object": "Jet",
        "name": "MyObservable",
        "value": None,
        "support_objects": "all",
    }
    assert Observable.from_name("Jet.MyObservable").fullname == obs.fullname
    assert Observable.from_config(obs.config).fullname == obs.fullname

    obs = Observable(physics_object="Jet0", support_objects=["single"])
    assert obs.support_objects == ["single"]

    obs = Observable(physics_object="Jet", support_objects=["collective"])
    obs = Observable(physics_object="Jet0.Particles", support_objects=["nested"])
    obs = Observable(physics_object="Jet0,Jet1", support_objects=["single", "multiple"])

    obs = Observable(physics_object="Jet0", support_objects=["single", "multiple"])
    obs._value = 0
    assert obs.value == 0


def test_bad_cases():
    with pytest.raises(TypeError):
        Observable(support_objects=["single"])

    with pytest.raises(TypeError):
        Observable(physics_object="Jet0", support_objects=["collective"])

    with pytest.raises(ValueError):
        Observable(physics_object="Jet0", support_objects=["wrong support object"])
