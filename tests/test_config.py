from hml.config import get_custom_objects_file_path, set_custom_objects_file_path


def test_get_custom_objects_file_path():
    assert get_custom_objects_file_path().as_posix() == "custom_objects.py"


def test_set_custom_objects_file_path():
    set_custom_objects_file_path("tests/saving/custom_objects.py")
    assert get_custom_objects_file_path().as_posix() == "tests/saving/custom_objects.py"
    assert get_custom_objects_file_path().exists()
