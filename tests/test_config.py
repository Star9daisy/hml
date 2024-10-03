from hml.config import (
    get_custom_objects_file_path,
    get_registry_file_path,
    set_custom_objects_file_path,
    set_registry_file_path,
)


def test_get_and_set_custom_objects_file_path(custom_objects_in_tests):
    set_custom_objects_file_path(custom_objects_in_tests)
    assert get_custom_objects_file_path().as_posix() == "tests/saving/custom_objects.py"


def test_get_and_set_registry_file_path(registry_in_tests):
    set_registry_file_path(registry_in_tests)
    assert get_registry_file_path().as_posix() == "tests/saving/registry.json"
