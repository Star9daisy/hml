import shutil
from pathlib import Path

import cppyy
import pytest

from hml.generators import Madgraph5, MG5Run


def test_Madgraph5():
    event_name1 = "pp2zj"
    generator1 = Madgraph5(
        executable="mg5_aMC",
        processes="p p > z j, z > j j",
        output_dir=f"./tests/data/{event_name1}",
        shower="Pythia8",
        detector="Delphes",
        settings={"nevents": 10, "iseed": 42},
    )
    event_name2 = "pp2wz"
    generator2 = Madgraph5(
        executable="mg5_aMC",
        definitions={"p": "p b b~", "j": "j b b~"},
        processes=["p p > w+ z, w+ > j j, z > ve ve~", "p p > w- z, w- > j j, z > ve ve~"],
        output_dir=f"./tests/data/{event_name2}",
        shower="Pythia8",
        detector="Delphes",
        settings={"nevents": 10, "iseed": 42, "htjmin": 400},
        cards=["./scripts/delphes_card_eflow.dat"],
    )

    generator1.launch()
    assert len(generator1.runs) == 1
    generator2.launch(new_output=True)
    generator2.launch()
    assert len(generator2.runs) == 2
    generator2.launch(new_output=True)
    assert len(generator1.runs) == 1

    expected1 = [
        "import model sm",
        "generate p p > z j, z > j j",
        f"output {Path.cwd() / 'tests/data/pp2zj'}",
        "launch",
        "    shower=Pythia8",
        "    detector=Delphes",
        "    set nevents 10",
        "    set iseed 42",
    ]
    expected2 = [
        "import model sm",
        "define p = p b b~",
        "define j = j b b~",
        "",
        "generate p p > w+ z, w+ > j j, z > ve ve~",
        "add process p p > w- z, w- > j j, z > ve ve~",
        f"output {Path.cwd() / 'tests/data/pp2wz'}",
        "launch",
        "    shower=Pythia8",
        "    detector=Delphes",
        "    set nevents 10",
        "    set iseed 42",
        "    set htjmin 400",
        f"    {Path.cwd() / 'scripts/delphes_card_eflow.dat'}",
    ]

    assert generator1.commands == expected1
    assert generator1.runs[0].cross_section != 0
    assert generator2.commands == expected2
    assert generator2.runs[0].cross_section != 0

    run = MG5Run(directory=Path.cwd() / f"tests/data/{event_name2}/Events/run_01")
    assert isinstance(run.events, cppyy.gbl.TTree)
    assert run.tag == "tag_1"
    assert run.cross_section != 0

    # Remove the output directories and log files
    shutil.rmtree(Path.cwd() / f"tests/data/{event_name1}", ignore_errors=True)
    Path.unlink(Path.cwd() / f"tests/data/{event_name1}.log", missing_ok=True)
    shutil.rmtree(Path.cwd() / f"tests/data/{event_name2}", ignore_errors=True)
    Path.unlink(Path.cwd() / f"tests/data/{event_name2}.log", missing_ok=True)


def test_wrong_executable():
    event_name1 = "pp2zj"
    with pytest.raises(EnvironmentError):
        generator = Madgraph5(
            executable="wrong_executable",
            processes="p p > z j, z > j j",
            output_dir=f"./tests/data/{event_name1}",
            shower="Pythia8",
            detector="Delphes",
        )
        generator.launch(new_output=True)

    event_name2 = 1111
    with pytest.raises(TypeError):
        generator = Madgraph5(
            executable="mg5_aMC",
            processes=1111,
            output_dir=f"./tests/data/{event_name2}",
            shower="Pythia8",
            detector="Delphes",
        )
        generator.launch(new_output=True)

    # Remove the output directories and log files
    shutil.rmtree(Path.cwd() / f"tests/data/{event_name1}", ignore_errors=True)
    Path.unlink(Path.cwd() / f"tests/data/{event_name1}.log", missing_ok=True)
    shutil.rmtree(Path.cwd() / f"tests/data/{event_name2}", ignore_errors=True)
    Path.unlink(Path.cwd() / f"tests/data/{event_name2}.log", missing_ok=True)