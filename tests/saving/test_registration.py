from custom_objects import NSubjettiness

from hml.saving.registration import init_registry, register, retrieve


def test_register():
    init_registry()
    tau21 = NSubjettiness(2, 1)
    register(tau21)


# def test_retrieve():
#     register(DummyClass)
#     register(DummyClass, name="dummy")
#     register(DummyClass, name="dm")

#     assert retrieve("dummy_class") == DummyClass
#     assert retrieve("dummy") == DummyClass
#     assert retrieve("dm").arg == DummyClass.from_name("dm").arg

#     assert len(retrieve(DummyClass)) > 1
