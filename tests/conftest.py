import pytest


@pytest.fixture
def root_events_path():
    return "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"


@pytest.fixture
def registry_in_tests():
    return "tests/saving/registry.json"


@pytest.fixture
def custom_objects_in_tests():
    return "tests/saving/custom_objects.py"
