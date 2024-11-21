import pytest
import uproot


@pytest.fixture
def events():
    path = "tests/data/pp2zz_42_pure_fatjet/Events/run_01/tag_1_delphes_events.root"
    events = uproot.open(path)["Delphes"]

    return events
