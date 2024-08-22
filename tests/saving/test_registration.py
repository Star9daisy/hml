from hml.saving.registration import ALL_REGISTERED_OBJECTS, register, retrieve


class DummyClass:
    def __init__(self, arg=None):
        self.arg = arg

    @property
    def config(self): ...

    @classmethod
    def from_config(cls, config): ...

    @property
    def name(self): ...

    @classmethod
    def from_name(cls, name):
        return cls(arg=name)


def dummy_function(): ...


def test_register():
    register(DummyClass)
    index = len(ALL_REGISTERED_OBJECTS) - 1
    assert ALL_REGISTERED_OBJECTS[index]["registered_name"] == "DummyClass"
    assert ALL_REGISTERED_OBJECTS[index]["is_for_init"] is False

    register(DummyClass, name="dummy")
    index = len(ALL_REGISTERED_OBJECTS) - 1
    assert ALL_REGISTERED_OBJECTS[index]["registered_name"] == "dummy"
    assert ALL_REGISTERED_OBJECTS[index]["is_for_init"] is False

    register(DummyClass, name="dummy", is_for_init=True)
    index = len(ALL_REGISTERED_OBJECTS) - 1
    assert ALL_REGISTERED_OBJECTS[index]["registered_name"] == "dummy"
    assert ALL_REGISTERED_OBJECTS[index]["is_for_init"] is True


def test_retrieve():
    register(DummyClass)
    register(DummyClass, name="dummy")
    register(DummyClass, name="dm", is_for_init=True)

    assert retrieve("DummyClass") == DummyClass
    assert retrieve("dummy") == DummyClass
    assert retrieve("dm").arg == DummyClass.from_name("dm").arg

    assert len(retrieve(DummyClass)) > 1
