from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Union

import cppyy
import ROOT
import yaml
from rich.console import Console
from rich.table import Table

import hml

ROOT.gSystem.Load("libDelphes")

PathLike = Union[str, Path, os.PathLike]


class Madgraph5:
    """Wrapper of Madgraph5 CLI to simulate colliding events.

    Madgraph5 is a wrapper class of Madgraph5 CLI. It turns the commands of
    CLI into parameters and methods. Users can use this class to generate
    events and get the information of each generated run.

    Parameters
    ----------
    executable: PathLike
        The executable file path of Madgraph5.
    output: PathLike
        The output directory of events that are about to be generated or already
        generated.
    model: PathLike
        The theory model to be used. It could be the model path or the model
        name under the models directory of Madgraph5.
    definitions: dict[str, str]
        The definitions of multiparticle.
    processes: list[str]
        The processes to be generated.
    shower: str
        The parton shower tool to be used. Only Pythia8 is supported currently.
    detector: str
        The detector simulation tool to be used. Only Delphes is supported
        currently.
    settings: dict[str, Any]
        The phase space and parameter settings.
    cards: list[PathLike]
        The shower and detector configuration cards to be used.
    n_events_per_subrun: int
        The number of events per subrun. The default is 100000. Events are
        generated by command `multi_run n_subruns`. The `n_events` in the
        settings are the total number of events. The `n_subruns` is calculated
        then to set the number of events for each subrun.

    Parameters correspond to commands in Madgraph5 CLI or options after
    launching generation in Madgraph5. Here is the correspondence table:

    | Parameters  | Madgraph5 commands or options    |
    |-------------|----------------------------------|
    | model       | import model command             |
    | definitions | define command                   |
    | processes   | generate & add process commands  |
    | output      | output command                   |
    | shower      | shower option                    |
    | detector    | detector option                  |
    | settings    | set command                      |
    | cards       | paths of cards                   |
    """

    def __init__(
        self,
        executable: PathLike,
        output: PathLike,
        model: PathLike = "sm",
        definitions: dict[str, str] = {},
        processes: list[str] = [],
        shower: str = "off",
        detector: str = "off",
        settings: dict[str, Any] = {},
        cards: list[PathLike] = [],
        n_events: int = 10000,
        seed: int = 42,
        tags: list[str] = [],
        n_events_per_subrun: int = 100000,
    ) -> None:
        # Before output ------------------------------------------------------ #
        # These parameters are required to be set once for all runs of the same
        # processes. So they cannot be changed after creating a generator.

        # Check if the executable exists
        if (_executable := shutil.which(executable)) is not None:
            self._executable = Path(_executable).resolve()
            self._mg5_dir = self._executable.parent.parent
        else:
            raise EnvironmentError(f"{executable} does not exist.")

        # Check if the model exists
        # Case 1: it's a model provided by HML (i.e. models in hml/theories)
        _hml_dir = Path(list(hml.__path__)[0])
        if (_model_dir := _hml_dir / f"theories/{model}").exists():
            with (_model_dir / "metadata.yml").open() as f:
                metadata = yaml.safe_load(f)
            self._model = (_model_dir / metadata["file"]).resolve()
        # Case 2: it's a model path provided by user (i.e. absolute path)
        elif (_model_file := Path(model)).exists():
            self._model = _model_file.resolve()
        # Case 3: it's a model provided by Madgraph5
        # There're three sources of models in Madgraph5:
        # 1. from the models directory
        # 2. from MG5aMC server
        # 3. from FeynRules website
        # Currently, these case are handled by Madgraph5 CLI so no error would
        # be raised here.
        else:
            self._model = model

        self._definitions = definitions
        self._processes = processes
        self._output = Path(output).resolve()

        # After output ------------------------------------------------------- #
        # These parameters can be changed when launching a new run.

        self.shower = shower
        self.detector = detector
        self.settings = settings
        self.cards = cards
        self.n_events = n_events
        self.seed = seed
        self.tags = tags
        self.n_events_per_subrun = n_events_per_subrun

    @property
    def executable(self) -> Path:
        """The executable file path of Madgraph5."""
        return self._executable

    @property
    def model(self) -> PathLike:
        """The theory model to be used."""
        return self._model

    @property
    def definitions(self) -> dict[str, str]:
        """The definitions of multiparticle."""
        return self._definitions

    @property
    def processes(self) -> list[str]:
        """The processes to be generated."""
        return self._processes

    @property
    def output(self) -> Path:
        """The output directory of events."""
        return self._output

    @property
    def shower(self) -> str:
        """The parton shower tool to be used."""
        return self._shower

    @shower.setter
    def shower(self, shower: str) -> None:
        if shower.lower() not in ["off", "pythia8"]:
            raise ValueError(f"Shower {shower} is not supported.")
        self._shower = shower

    @property
    def detector(self) -> str:
        """The detector simulation tool to be used."""
        return self._detector

    @detector.setter
    def detector(self, detector: str) -> None:
        if detector.lower() not in ["off", "delphes"]:
            raise ValueError(f"Detector {detector} is not supported.")
        self._detector = detector

    @property
    def settings(self) -> dict[str, Any]:
        """The phase space and parameter settings."""
        return self._settings

    @settings.setter
    def settings(self, settings: dict[str, Any]) -> None:
        self._settings = settings

    @property
    def cards(self) -> list[Path]:
        """The shower and detector configuration cards to be used."""
        return self._cards

    @cards.setter
    def cards(self, cards: list[PathLike]) -> None:
        self._cards = []
        _cards = [Path(card).resolve() for card in cards]
        for card in _cards:
            if not card.exists():
                raise FileNotFoundError(f"Card {card} does not exist.")

        if self.shower == "Pythia8":
            use_default_pythia8_card = True
            for card in _cards:
                if "pythia8" in card.name:
                    use_default_pythia8_card = False
                    self.cards.append(card)
            if use_default_pythia8_card:
                self.cards.append(
                    self._mg5_dir / "Template/LO/Cards/pythia8_card_default.dat"
                )

        if self.detector == "Delphes":
            use_default_delphes_card = True
            for card in _cards:
                if "delphes" in card.name:
                    use_default_delphes_card = False
                    self.cards.append(card)
            if use_default_delphes_card:
                self.cards.append(
                    self._mg5_dir / "Template/Common/Cards/delphes_card_default.dat"
                )

    @property
    def n_events(self) -> int:
        """The number of events."""
        return self._n_events

    @n_events.setter
    def n_events(self, n_events: int) -> None:
        self._n_events = n_events
        self.settings["nevents"] = n_events

    @property
    def seed(self) -> int:
        """The random seed."""
        return self._seed

    @seed.setter
    def seed(self, seed: int) -> None:
        self._seed = seed
        self.settings["iseed"] = seed

    @property
    def tags(self) -> list[str]:
        """The tags of runs."""
        return self._tags

    @tags.setter
    def tags(self, tags: list[str]) -> None:
        if len(tags) == 0:
            tags = ["no_tags"]
        self._tags = tags
        self.settings["run_tag"] = ",".join(tags)

    @property
    def n_events_per_subrun(self) -> int:
        """The number of events per subrun."""
        return self._n_events_per_subrun

    @n_events_per_subrun.setter
    def n_events_per_subrun(self, n_events_per_subrun: int) -> None:
        self._n_events_per_subrun = n_events_per_subrun
        if n_events_per_subrun > self.n_events:
            self.settings["nevents"] = self.n_events
        else:
            self.settings["nevents"] = n_events_per_subrun

    @property
    def n_subruns(self) -> int:
        """The number of subruns."""
        if self.n_events_per_subrun >= self.n_events:
            return 1

        n_subruns, rest_runs = divmod(self.n_events, self.n_events_per_subrun)
        if rest_runs != 0:
            return n_subruns + 1
        else:
            return n_subruns

    @property
    def commands(self) -> list[str]:
        """Commands converted from parameters to be executed in Madgraph5."""
        settings = self.settings.copy()
        settings["nevents"] = self.n_events_per_subrun

        # The commands will be executed in the run directory so all paths are
        # the current directory.
        commands = [
            *[f"import model {self.model}"],
            *[f"define {k} = {v}" for k, v in self.definitions.items()],
            *[f"generate {self.processes[0]}"],
            *[f"add process {p}" for p in self.processes[1:]],
            *["output mg5_output"],
            *["launch -i"],
            *[f"multi_run {self.n_subruns}"],
            *[f"shower={self.shower}"],
            *[f"detector={self.detector}"],
            *[f"set {k} {v}" for k, v in settings.items()],
            *[f"{card}" for card in self.cards],
            *["print_results --path=results --format=short"],
        ]

        return commands

    @property
    def runs(self) -> list[MG5Run]:
        """Madgraph5 runs of all launches."""
        run_dirs = [i for i in self.output.glob("run_*") if i.is_dir()]
        run_dirs = sorted(run_dirs, key=lambda x: int(x.name.split("_")[1]))
        runs = [MG5Run(i) for i in run_dirs]
        return runs

    def summary(self) -> None:
        """Summary of all runs."""
        console = Console()
        table = Table(
            title="\n".join(self.processes),
            caption=f"Output: {self.output.absolute().relative_to(Path.cwd())}",
        )

        table.add_column("#", justify="right")
        table.add_column("Name")
        table.add_column("Tags")
        table.add_column("Cross section (pb)", justify="center")
        table.add_column("N events", justify="right")
        table.add_column("Seed", justify="right")

        for i, run in enumerate(self.runs):
            table.add_row(
                f"{i}",
                f"{run.name}[{run.n_subruns}]",
                f"{run.tag}",
                f"{run.cross_section:.3e} +- {run.error:.3e}",
                f"{run.n_events:,}",
                f"{run.seed}",
            )

        console.print(table)

    def launch(
        self,
        new_output: bool = False,
        show_status: bool = True,
    ) -> None:
        """Launch Madgraph5 to generate events.

        Parameters
        ----------
        new_output: bool
            If True, remove the existing output directory and create a new one.
        show_status: bool
            If True, print the status of the launched run, else launch silently.
        """
        # The structure of the output directory is:
        # <output>/
        #     run_1/
        #         madevent/Events/run_01/tag_1_delphes_events.root
        #         run.log
        #         commands
        #         tag
        #         cards
        #         results
        #     ...
        # The madevent directory is the one that Madgraph5 actually outputs.
        # Here we mainly restrict one madevent only contains one run so that
        # we can safely reproduce this run.
        # This kind of structure is now called one run.

        # Prepare the output directory
        if new_output or not self.output.exists():
            shutil.rmtree(self.output, ignore_errors=True)
            self.output.mkdir(parents=True, exist_ok=True)

        # Check the current run number
        run_dir = self._get_next_run_dir()
        run_dir.mkdir()
        log_path = run_dir / "run.log"
        seed_path = run_dir / "seed"
        with seed_path.open("w") as f:
            f.write(f"{self.seed}")

        commands_path = run_dir / "commands"
        cards_dir = run_dir / "cards"
        cards_dir.mkdir()

        pythia8_card = None
        delphes_card = None
        for i, card in enumerate(self.cards):
            actual_card_path = Path(shutil.copy(card, cards_dir))
            # If it is a pythia8 card, set the random seed
            if actual_card_path.name.startswith("pythia8"):
                pythia8_card = actual_card_path
                with actual_card_path.open() as f:
                    lines = f.readlines()

                # For pythia8 cards, it's required two settings for random seed:
                # 1. Random:setSeed = on
                # 2. Random:seed = <an integer>
                set_seed = False
                found_seed = False
                for i, line in enumerate(lines):
                    if line.startswith("Random:setSeed = on"):
                        set_seed = True
                    if line.startswith("Random:seed"):
                        found_seed = True
                        lines[i] = f"Random:seed = {self.seed}\n"

                if not set_seed:
                    lines.append("Random:setSeed = on\n")
                    lines.append(f"Random:seed = {self.seed}\n")
                elif not found_seed:
                    lines.append(f"Random:seed = {self.seed}\n")

                # Write back with the new random seed
                with actual_card_path.open("w") as f:
                    f.writelines(lines)

            # If it is a delphes card, set the random seed
            elif actual_card_path.name.startswith("delphes"):
                delphes_card = actual_card_path
                with actual_card_path.open() as f:
                    lines = f.readlines()

                # For delphes cards, there's no way in official documentation to
                # set the random seed. However, I found some examples in its
                # GitHub repository: check the following folder in the repository:
                # 1. cards/delphes_card_CLD.tcl
                # 2. cards/FCC/scenarios/FCChh_I.tcl
                # It seems like `set RandomSeed <an integer>` at the beginning
                # is a way to set the random seed. This is what we do here.
                found_seed = False
                for i, line in enumerate(lines):
                    if line.startswith("set RandomSeed"):
                        lines[i] = f"set RandomSeed {self.seed}\n"
                        found_seed = True

                if not found_seed:
                    lines = [f"set RandomSeed {self.seed}\n"] + lines

                # Write back with the new random seed
                with actual_card_path.open("w") as f:
                    f.writelines(lines)

        actual_commands = self.commands.copy()
        for i, line in enumerate(actual_commands):
            if len(line.split(" ")) == 1:
                if "pythia8" in line and pythia8_card:
                    actual_commands[i] = pythia8_card.as_posix()
                if "delphes" in line and delphes_card:
                    actual_commands[i] = delphes_card.as_posix()

        with commands_path.open("w") as f:
            f.write("\n".join(actual_commands))

        # Launch Madgraph5 and redirect output to the log file
        with log_path.open("w") as f:
            process = subprocess.Popen(
                f"{self.executable} {commands_path}",
                cwd=run_dir,
                shell=True,
                stdout=f,
                stderr=subprocess.PIPE,
            )

        # Check and print status
        status = ""
        while (status != "Done") or process.poll() is None:
            # Madgraph5 generate py.py not only at the beginning but also the
            # middle of launching.
            if (redundant_path := Path(run_dir / "py.py")).exists():
                redundant_path.unlink(missing_ok=True)

            last_status = self._check_status(log_path, status)
            if last_status != status:
                if show_status and last_status != "":
                    print(last_status)
                status = last_status
            if status == "Failed":
                stderr = (
                    process.stderr.readline().decode().strip()
                    if process.stderr is not None
                    else ""
                )
                if "stty" in stderr or stderr == "":
                    status = "Done"
                    continue
                else:
                    raise RuntimeError(stderr)

    def remove(self, name: str) -> None:
        """Remove one run."""
        paths = self.output.glob(name + "*")
        for i in paths:
            if i.is_dir():
                shutil.rmtree(i)
            else:
                i.unlink()

    def clean(self) -> None:
        """Remove the output directory."""
        for run in self.runs:
            run.events.Reset()

        shutil.rmtree(self.output)

    def _get_next_run_dir(self) -> Path:
        """The next run directory."""
        all_dirs = [i for i in self.output.glob("run_*") if i.is_dir()]
        n_runs = len(all_dirs)
        run_dir = self.output / f"run_{n_runs + 1}"
        return run_dir

    def _check_status(self, log, current_status: str) -> str:
        """Check the status of the launched run."""
        with open(log, "r") as f:
            contents = f.readlines()

        last_status = ""
        for line in contents[::-1]:
            if line.startswith("Generating"):
                last_status = "Generating events..."
                break
            elif "Running Pythia8" in line:
                last_status = "Running Pythia8..."
                break
            elif "Running Delphes" in line:
                last_status = "Running Delphes..."
                break
            elif "INFO: storing files" in line:
                last_status = "Storing files..."
                break
            elif line.startswith("INFO: Done"):
                last_status = "Done"
                break
            elif line.startswith("quit") and current_status != "Done":
                last_status = "Failed"
                break

        return last_status


class MG5Run:
    """MG5Run stores the information of a Madgraph5 run.

    Parameters
    ----------
    dir: PathLike
        The directory path to a run.
    """

    def __init__(self, dir: PathLike):
        _dir = Path(dir)
        if not _dir.exists():
            raise FileNotFoundError(f"Directory {_dir} does not exist.")
        self._dir = _dir
        self._name = _dir.name
        self._seed = int((_dir / "seed").read_text())

        self._events = ROOT.TChain("Delphes")
        self._n_subruns = 0
        for i in self.dir.glob("mg5_output/Events/run_01_*"):
            if i.is_dir():
                self._n_subruns += 1

        root_files = list((self.dir / "mg5_output/Events").glob("**/*.root"))
        for file in root_files:
            self._events.Add(file.as_posix())

        # results.txt are updated each time a generator finishes running.
        # New run results are appended to the end of the file.
        # So we need to read the line that the run_name is exactly the same with
        # the run name of the instance.
        results = self.dir / "results"
        info = []
        with open(results, "r") as f:
            for result in f:
                # When generating events using `multi_run 1`,
                # runs are:
                # - run_01
                # - run_01_0
                # It's ok to use `print_results` command to get the info.
                # But if we `launch -i` the same output to generate run_02 and
                # its subruns, the `print_results` command will correctly print
                # the info of run_02, but the info of run_01 will be lost except
                # the info of run_01_0.
                # Since we refactor the output structure since v0.2.2 and one
                # output only contains one run, we can safely search for the
                # info via `run_01`

                # The first five columes in results.txt are:
                # run_name tag cross error Nb_event
                # In HML, they are renamed to: name, tag, cross_section, error,
                # n_events. As "name" is also the name of run directory (e.g.
                # the run_01 is the "run_name" and also the run directory), here
                # we only catch the four columns after run_name.
                if result.startswith("run_01"):
                    info = result.split()
                    break
        if not info:
            raise RuntimeError(f"Info of {self._name} not found in {results}.")

        self._tag = info[1]
        self._cross_section = float(info[2])
        self._error = float(info[3])
        self._n_events = int(info[4])

    @property
    def dir(self) -> Path:
        """The directory path to a run."""
        return self._dir

    @property
    def name(self) -> str:
        """The name of a run, e.g. run_01, run_02... by default."""
        return self._name

    @property
    def tag(self) -> str:
        """The run tag."""
        return self._tag

    @property
    def cross_section(self) -> float:
        """Cross section of a run."""
        return self._cross_section

    @property
    def error(self) -> float:
        """Error of the cross section."""
        return self._error

    @property
    def n_events(self) -> int:
        """Number of events generated in a run."""
        return self._n_events

    @property
    def n_subruns(self) -> int:
        """Number of subruns in a run, e.g. run_01_0, run_01_1... by default."""
        return self._n_subruns

    @property
    def events(self) -> cppyy.gbl.TChain:
        """Events read by PyROOT of a run."""
        return self._events

    @property
    def seed(self) -> int:
        """The random seed of a run."""
        return self._seed
