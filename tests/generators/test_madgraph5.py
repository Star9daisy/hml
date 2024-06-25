import shutil
import unittest
from pathlib import Path

import pexpect
import pytest

from hml.generators import Madgraph5, Madgraph5Run


class TestMadgraph5(unittest.TestCase):
    def test_default(self):
        g = Madgraph5()

        # executable...✘
        # verbose...✔
        with pytest.raises(ValueError):
            g.executable
        assert g.verbose == 1

        # home...✔
        # version...✔
        # child...✘
        # processes...✘
        # output_dir...✘
        # runs...✘
        assert g.home is None
        assert g.version is None
        with pytest.raises(AttributeError):
            g.child
        with pytest.raises(AttributeError):
            g.processes
        with pytest.raises(AttributeError):
            g.output_dir
        with pytest.raises(AttributeError):
            g.runs

    def test_executable(self):
        g = Madgraph5()

        # Setter -> None
        g.executable = None
        assert g._executable is None

        # Setter -> str | Path
        # Good
        g.executable = "mg5_aMC"
        assert isinstance(g._executable, Path)
        assert isinstance(g._child, pexpect.spawn)
        assert isinstance(g._version, str)
        # Bad
        with pytest.raises(FileNotFoundError):
            g.executable = "unknown"

        # Setter -> invalid type
        with pytest.raises(TypeError):
            g.executable = 1

        # Getter -> None
        # Bad
        g.executable = None
        with pytest.raises(ValueError):
            g.executable

        # Getter -> str | Path
        # Good
        g.executable = "mg5_aMC"
        assert isinstance(g.executable, Path)
        assert isinstance(g.child, pexpect.spawn)
        assert isinstance(g.home, Path)
        assert isinstance(g.version, str)

    def test_verbose(self):
        g = Madgraph5()

        # Setter -> int
        # Good
        g.verbose = 0
        assert g._verbose == 0
        # Bad
        with pytest.raises(ValueError):
            g.verbose = -1

        # Setter -> invalid type
        with pytest.raises(ValueError):
            g.verbose = "0"

        # Getter -> int
        g.verbose = 0
        assert g.verbose == 0

    def test_import_model(self):
        g = Madgraph5(executable="mg5_aMC")

        # Good
        g.import_model("sm")
        g.import_model(g.home / "models" / "sm")
        if not (g.home / "models" / "heft").exists():
            g.import_model("heft")
            shutil.rmtree(g.home / "models" / "heft")

        # Bad
        with pytest.raises(ValueError):
            g.import_model("non_ex")

        with pytest.raises(ValueError):
            g.import_model("non-existent-model")

        Path("MG5_debug").unlink()

    def test_define(self):
        g = Madgraph5(executable="mg5_aMC")

        # Good
        g.define(["j = j b b~"])

        # Bad
        with pytest.raises(ValueError):
            g.define(["j = "])

    def test_generate(self):
        g = Madgraph5(executable="mg5_aMC")

        # Good
        g.generate(["p p > t t~"])
        g.generate(["p p > w+ j", "p p > w- j"])

        # Bad
        with pytest.raises(ValueError):
            g.generate(["p p > "])

        with pytest.raises(ValueError):
            g.generate(["p p > w+ j", "p p >"])

    def test_display_diagrams(self):
        g = Madgraph5(executable="mg5_aMC")

        # Bad
        with pytest.raises(ValueError):
            g.display_diagrams()

        shutil.rmtree("Diagrams")
        Path("MG5_debug").unlink()

        g.generate(["p p > t t~"])

        # Good
        g.display_diagrams("/tmp/Diagrams")
        g.display_diagrams("/tmp/Diagrams")

        # Bad
        with pytest.raises(FileExistsError):
            g.display_diagrams("/tmp/Diagrams", overwrite=False)

        shutil.rmtree("/tmp/Diagrams")

    def test_output(self):
        g = Madgraph5(executable="mg5_aMC")

        # Bad
        with pytest.raises(ValueError):
            g.output()

        g.generate(["p p > t t~"])

        # Good
        g.output()
        g.output("/tmp/pp2tt")

        shutil.rmtree("PROC_sm_0")
        shutil.rmtree("/tmp/pp2tt")

    def test_launch(self):
        g = Madgraph5(executable="mg5_aMC")

        # Bad
        with pytest.raises(AttributeError):
            g.launch()

        # Good
        g.generate(["p p > t t~"])
        g.output("/tmp/pp2tt")

        # Dry run to test the random seed settings in cards
        # 1. Default cards
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            dry=True,
        )

        # 2. Specified cards
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            cards=[
                "./tests/scripts/pythia8_card.dat",
                "./tests/scripts/delphes_card.dat",
            ],
            dry=True,
        )

        # 3. Modify existing seed in pythia8 card
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            cards=[
                "./tests/scripts/pythia8_card_existing_seed.dat",
                "./tests/scripts/delphes_card.dat",
            ],
            dry=True,
        )

        # 4. Add missing seed in pythia8 card when already "setSeed"
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            cards=[
                "./tests/scripts/pythia8_card_incomplete_seed.dat",
                "./tests/scripts/delphes_card.dat",
            ],
            dry=True,
        )

        # 5. Modify existing seed in delphes card
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            cards=[
                "./tests/scripts/pythia8_card.dat",
                "./tests/scripts/delphes_card_existing_seed.dat",
            ],
            dry=True,
        )

        # Normal run
        # Good
        g.generate(["p p > t t~"])
        g.output("/tmp/pp2tt")
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            multi_run=2,
        )
        g.summary()

        g.generate(["p p > t t~"])
        g.output("pp2tt")
        g.launch(
            shower="pythia8",
            detector="delphes",
            settings={"nevents": 100},
            seed=42,
            multi_run=2,
        )
        g.summary()

        # Bad
        g.generate(["p p > t t~"])
        g.output("pp2tt")
        with pytest.raises(ValueError):
            g.launch(
                shower="unknown",
                detector="delphes",
                settings={"nevents": 100},
                seed=42,
                multi_run=2,
            )

        shutil.rmtree("pp2tt")

    def test_from_output(self):
        # Good
        g = Madgraph5.from_output("./tests/data/pp2tt")

        assert len(g.runs) == 2
        assert g.processes == ["p p > t t~"]

        # Bad
        with pytest.raises(FileNotFoundError):
            Madgraph5.from_output("unknown")


class TestMadgraph5Run(unittest.TestCase):
    def test_pp2tt(self):
        # Good
        run = Madgraph5Run(output_dir="./tests/data/pp2tt", name="run_01")
        assert run.directory == Path("./tests/data/pp2tt/Events/run_01")
        assert run.name == "run_01"
        assert run.collider == "pp:6500.0x6500.0"
        assert run.tag == "tag_1"
        assert run.seed == 42
        assert run.cross == 503.6
        assert run.error == 2.8
        assert run.n_events == 100
        assert len(run.sub_runs) == 0
        assert len(run.events()) == 1

        run = Madgraph5Run(output_dir="./tests/data/pp2tt", name="run_02")
        assert run.directory == Path("./tests/data/pp2tt/Events/run_02")
        assert run.name == "run_02"
        assert run.collider == "pp:6500.0x6500.0"
        assert run.tag == "tag_1"
        assert run.seed == 48
        assert run.cross == 504.2
        assert run.error == 2
        assert run.n_events == 200
        assert len(run.sub_runs) == 2
        assert len(run.events()) == 2

        # Bad
        with pytest.raises(FileNotFoundError):
            Madgraph5Run(output_dir="./tests/data/pp2tt", name="run_03")

        with pytest.raises(ValueError):
            run = Madgraph5Run(output_dir="./tests/data/pp2tt", name="run_01")
            run.events("lhe")

    def test_special_methods(self):
        run = Madgraph5Run(output_dir="./tests/data/pp2tt", name="run_02")

        assert (
            repr(run)
            == "Madgraph5Run run_02 (2 sub runs):\n- collider: pp:6500.0x6500.0\n- tag: tag_1\n- seed: 48\n- cross: 504.2\n- error: 2.0\n- n_events: 200"
        )
