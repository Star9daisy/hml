import pytest
from custom_objects import NSubjettiness

from hml.config import REGISTRY_FILE_PATH, set_registry_file_path
from hml.saving.registration import (
    init_registry,
    register,
    retrieve,
    show_custom_registered_objects,
)

set_registry_file_path("tests/saving/registry.json")


def test_register():
    init_registry()
    tau21 = NSubjettiness(2, 1)
    register(tau21)

    with pytest.raises(ValueError):
        register(tau21)


def test_retrieve():
    init_registry()
    retrieved = retrieve("tau21")
    assert isinstance(retrieved, NSubjettiness)

    tau21 = NSubjettiness(2, 1)
    register(tau21, "my_tau")
    retrieved = retrieve("my_tau")
    assert isinstance(retrieved, NSubjettiness)

    retrieved = retrieve(NSubjettiness)
    assert len(retrieved) == 2


def test_show_custom_registered_objects():
    show_custom_registered_objects()


set_registry_file_path(REGISTRY_FILE_PATH)