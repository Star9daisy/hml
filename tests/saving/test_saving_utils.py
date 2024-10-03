from hml.config import set_custom_objects_file_path
from hml.saving.registration import CUSTOM_REGISTERED_OBJECTS
from hml.saving.utils import import_custom_objects


def test_import_custom_objects(custom_objects_in_tests):
    set_custom_objects_file_path(custom_objects_in_tests)
    import_custom_objects()

    all_registered_names = [obj["registered_name"] for obj in CUSTOM_REGISTERED_OBJECTS]
    assert r"tau(?P<m>\d)(?P<n>\d)" in all_registered_names
