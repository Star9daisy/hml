import shutil
from pathlib import Path

import pytest

from hml.generators import Madgraph5, MG5Run
from hml.observables import (
    DeltaR,
    E,
    Eta,
    M,
    Observable,
    Phi,
    Pt,
    Px,
    Py,
    Pz,
    get_lorentzvector_values,
    resolve_shortname,
)


def test_resolve_shortname():
    assert resolve_shortname("Jet") == (["Jet"], [-1])
    assert resolve_shortname("Jet1") == (["Jet"], [0])
    assert resolve_shortname("Muon1") == (["Muon"], [0])
    assert resolve_shortname("Muon2") == (["Muon"], [1])
    assert resolve_shortname("Jet1+Jet2") == (["Jet", "Jet"], [0, 1])
    assert resolve_shortname("Jet1+Jet2+Jet3") == (["Jet", "Jet", "Jet"], [0, 1, 2])
    assert resolve_shortname("Jet1+Muon1") == (["Jet", "Muon"], [0, 0])

    with pytest.raises(ValueError):
        resolve_shortname("Jet0")
    with pytest.raises(ValueError):
        resolve_shortname("*Jet")


def test_observables():
    event_name = "pp2zj_"
    generator = Madgraph5(
        executable="mg5_aMC",
        processes=["p p > z j, z > j j"],
        output=f"./tests/data/{event_name}",
        shower="Pythia8",
        detector="Delphes",
        settings={"nevents": 10, "iseed": 42},
    )
    generator.launch()

    run = MG5Run(f"tests/data/{event_name}/madevent_1")
    event = next(iter(run.events))

    for obs in [Pt, M, Eta, Phi, Px, Py, Pz, E]:
        assert issubclass(obs, Observable)
        for shortname in ["Jet", "Jet1", "Jet2"]:
            a = obs(shortname)
            a.from_event(event)
            assert a.values is not None

    assert issubclass(DeltaR, Observable)
    obs = DeltaR("Jet1", "Jet2")
    obs.from_event(event)
    assert obs.values is not None

    assert len(get_lorentzvector_values(event, "Pt", ["Jet"], [-1])) == event.Jet_size
    with pytest.raises(ValueError):
        get_lorentzvector_values(event, "Pt", ["Jet"], [1, 2])
    with pytest.raises(IndexError):
        get_lorentzvector_values(event, "Pt", ["Jet"], [event.Jet_size + 1])

    # Clean up
    del run
    generator.clean()
