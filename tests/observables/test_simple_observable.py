from hml.observables.observable import Observable


class SimpleObservable(Observable): ...


def test_simple_observable():
    obs = SimpleObservable()
    assert obs.physics_object is None
    assert obs.name == "simple_observable"
    assert obs.config == {"physics_object": None, "name": "simple_observable"}
    assert SimpleObservable.from_config(obs.config).config == obs.config
