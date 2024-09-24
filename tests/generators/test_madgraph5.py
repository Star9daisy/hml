import shutil
from pathlib import Path

import pytest

from hml.generators.madgraph5 import Madgraph5


def test_madgraph5_init_default():
    g = Madgraph5()
    # Default attributes
    assert g.executable is None
    assert g.verbose == 1

    # Related to _spawn_child
    assert g.child is None
    assert g.version is None

    # Related to import_model
    assert hasattr(g, "model")
    assert hasattr(g, "model_dir")

    # Related to define
    assert not hasattr(g, "definitions")

    # Related to generate
    assert not hasattr(g, "processes")

    # Related to display_diagrams
    assert not hasattr(g, "diagrams_dir")

    # Related to output
    assert not hasattr(g, "output_dir")

    with pytest.raises(AttributeError):
        g.runs


def test_madgraph5_init_executable():
    g = Madgraph5(executable="mg5_aMC")

    assert "mg5_aMC" in g.executable
    assert g.version == "3.4.2"


def test_madgraph5_import_model():
    g = Madgraph5("mg5_aMC")

    g.import_model("sm")
    assert g.model == "sm"
    assert "sm" in g.model_dir

    with pytest.raises(ValueError):
        g.import_model("unknown")

    Path("MG5_debug").unlink()


def test_madgraph5_define():
    g = Madgraph5("mg5_aMC")

    g.define({"p": "g u c d s u~ c~ d~ s~"})
    assert "p" in g.multi_particles
    assert g.multi_particles["p"] == "g u c d s u~ c~ d~ s~"

    with pytest.raises(ValueError):
        g.define({"t": "t t~"})


def test_madgraph5_generate():
    g = Madgraph5("mg5_aMC")

    g.generate(["p p > t t~"])
    assert g.processes == ["p p > t t~"]

    g.generate(["p p > w+ j", "p p > w- j"])
    assert g.processes == ["p p > w+ j", "p p > w- j"]

    with pytest.raises(ValueError):
        g.generate(["p p >"])


def test_madgraph5_display_diagrams():
    g = Madgraph5("mg5_aMC")
    g.generate(["p p > t t~"])

    g.display_diagrams("/tmp/Diagrams")
    assert Path("/tmp/Diagrams").exists()
    assert Path("/tmp/Diagrams").exists()  # Overwrite

    with pytest.raises(FileExistsError):
        g.display_diagrams("/tmp/Diagrams", overwrite=False)


def test_madgraph5_output():
    g = Madgraph5("mg5_aMC")
    g.generate(["p p > t t~"])

    # Good #1: Use default madevent name
    if Path("PROC_sm_0").exists():
        shutil.rmtree("PROC_sm_0")
    g.output()
    assert Path("PROC_sm_0").exists()

    # Good #2: Use custom name
    g.output("/tmp/pp2tt")
    g.output("/tmp/pp2tt")  # Overwrite
    assert Path("/tmp/pp2tt").exists()

    # Bad: Directory already exists
    with pytest.raises(FileExistsError):
        g.output("/tmp/pp2tt", overwrite=False)

    # Clean
    shutil.rmtree("PROC_sm_0")
    shutil.rmtree("/tmp/pp2tt")


def test_madgraph5_launch():
    g = Madgraph5("mg5_aMC")
    g.generate(["p p > t t~"])
    g.output("/tmp/pp2tt")

    # Dry run to test the random seed settings in cards
    # 1. Default cards
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        dry_run=True,
    )

    # 2. Custom cards
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        cards={
            "pythia8": "./tests/scripts/pythia8_card.dat",
            "delphes": "./tests/scripts/delphes_card.dat",
        },
        dry_run=True,
    )

    # 3. Modify existing seed in pythia8 card
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        cards={
            "pythia8": "./tests/scripts/pythia8_card_existing_seed.dat",
            "delphes": "./tests/scripts/delphes_card.dat",
        },
        dry_run=True,
    )

    # 4. Add missing seed in pythia8 card when already "setSeed"
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        cards={
            "pythia8": "./tests/scripts/pythia8_card_incomplete_seed.dat",
            "delphes": "./tests/scripts/delphes_card.dat",
        },
        dry_run=True,
    )

    # 5. Modify existing seed in delphes card
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        cards={
            "pythia8": "./tests/scripts/pythia8_card.dat",
            "delphes": "./tests/scripts/delphes_card_existing_seed.dat",
        },
        dry_run=True,
    )

    # Normal run
    # Change the verbose to cover the case
    g = Madgraph5("mg5_aMC", verbose=1)
    g.import_model("sm")
    g.define({"p": "g u c d s u~ c~ d~ s~"})
    g.generate(["p p > t t~"])
    g.output("/tmp/pp2tt")
    g.display_diagrams("/tmp/Diagrams")
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        multi_run=2,
    )
    g.summary()

    # Relative path will be shown in the summary
    g = Madgraph5("mg5_aMC", verbose=2)
    g.import_model("sm")
    g.define({"p": "g u c d s u~ c~ d~ s~"})
    g.generate(["p p > t t~"])
    g.output("pp2tt")
    g.display_diagrams("Diagrams")
    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
    )
    g.summary()

    # Clean
    shutil.rmtree("/tmp/pp2tt")
    shutil.rmtree("/tmp/Diagrams")
    shutil.rmtree("pp2tt")
    shutil.rmtree("Diagrams")


def test_madgraph5_from_output():
    # Good
    g = Madgraph5.from_output("./tests/data/pp2zz_42_pure_fatjet_2_subruns")
    assert len(g.runs[0].sub_runs) == 2

    # Bad
    with pytest.raises(FileNotFoundError):
        Madgraph5.from_output("./tests/data/unknown")
