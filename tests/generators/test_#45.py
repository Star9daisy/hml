import shutil

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
