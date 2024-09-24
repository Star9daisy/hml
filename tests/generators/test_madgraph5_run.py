from pathlib import Path

import pytest

from hml.generators.madgraph5 import Madgraph5Run


def test_madgraph5_run():
    # Single run
    output_dir = "tests/data/pp2zz_42_pure_fatjet"
    run = Madgraph5Run(output_dir, "run_01")
    assert run.directory == Path(output_dir) / "Events/run_01"
    assert run.name == "run_01"
    assert run.collider == "pp:6500.0x6500.0"
    assert run.tag == "tag_1"
    assert run.seed == 42
    assert run.cross == 0.002284
    assert run.error == 3.8e-05
    assert run.n_events == 100
    assert run.sub_runs == []
    assert run.event_paths() == {
        "lhe": [],
        "hepmc": [],
        "root": [Path(output_dir) / "Events/run_01/tag_1_delphes_events.root"],
    }
    assert (
        repr(run)
        == "Madgraph5Run run_01:\n- collider: pp:6500.0x6500.0\n- tag: tag_1\n- seed: 42\n- cross: 0.002284\n- error: 3.8e-05\n- n_events: 100"
    )

    # Multi run
    output_dir = "tests/data/pp2zz_42_pure_fatjet_2_subruns"
    run = Madgraph5Run(output_dir, "run_01")
    assert run.directory == Path(output_dir) / "Events/run_01"
    assert run.name == "run_01"
    assert run.collider == "pp:6500.0x6500.0"
    assert run.tag == "tag_1"
    assert run.seed == 42
    assert run.cross == 0.002323
    assert run.error == 2.5e-05
    assert run.n_events == 200
    assert len(run.sub_runs) == 2
    assert run.event_paths()["lhe"] == []
    assert run.event_paths()["hepmc"] == []
    assert (
        Path(output_dir) / "Events/run_01_0/tag_1_delphes_events.root"
        in run.event_paths()["root"]
    )
    assert (
        Path(output_dir) / "Events/run_01_1/tag_1_delphes_events.root"
        in run.event_paths()["root"]
    )

    assert (
        repr(run)
        == "Madgraph5Run run_01 (2 sub runs):\n- collider: pp:6500.0x6500.0\n- tag: tag_1\n- seed: 42\n- cross: 0.002323\n- error: 2.5e-05\n- n_events: 200"
    )

    # Bad case: no banner file
    output_dir = "tests/data/pp2zz_42_pure_fatjet_no_banner"
    with pytest.raises(FileNotFoundError):
        Madgraph5Run(output_dir, "run_01")
