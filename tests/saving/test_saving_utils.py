from hml.config import set_custom_objects_file_path
from hml.saving.registration import ALL_REGISTERED_OBJECTS
from hml.saving.utils import import_custom_objects


def test_import_custom_objects():
    set_custom_objects_file_path("tests/saving/custom_objects.py")
    import_custom_objects()

    all_registered_names = [obj["registered_name"] for obj in ALL_REGISTERED_OBJECTS]
    assert "toy" in all_registered_names
