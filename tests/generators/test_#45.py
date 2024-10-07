import shutil
from pathlib import Path

from hml.generators import Madgraph5


def test_output_with_diagrams():
    g = Madgraph5(executable="mg5_aMC")
    g.generate(["p p > t t~"])

    g.output()
    assert g.diagrams_dir.parent.name == "PROC_sm_0"

    g.output("data/pp2tt")
    assert g.diagrams_dir.parent.name == "pp2tt"

    shutil.rmtree("PROC_sm_0")
    shutil.rmtree("data/pp2tt")


def test_log():
    g = Madgraph5(executable="mg5_aMC", verbose=1)
    assert "Loading default model: sm" in g.log

    g.define({"p": "p b b~"})
    assert "define p = p b b~" in g.log

    g.import_model("sm")
    assert "import model sm" in g.log

    g.generate(["p p > t t~"])
    assert "generate p p > t t~" in g.log

    g.display_diagrams()

    g.output("data/pp2tt")
    assert "output data/pp2tt -f" in g.log

    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
    )
    assert Path("data/pp2tt/Logs/run_1.log").exists()

    g.launch(
        shower="pythia8",
        detector="delphes",
        settings={"nevents": 100},
        seed=42,
        multi_run=2,
    )
    assert Path("data/pp2tt/Logs/run_2.log").exists()

    shutil.rmtree("Diagrams")
    shutil.rmtree("data/pp2tt")
