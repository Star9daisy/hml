import pytest

from hml.events import ROOTEvents, load_events


def test_load_events():
    # Good
    assert isinstance(load_events("tag_1_delphes_events.root"), ROOTEvents)
    # Bad
    with pytest.raises(ValueError):
        load_events("tag_1_delphes_events.root.txt")
