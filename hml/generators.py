from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
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
        shower: str = "Pythia8",
        detector: str = "Delphes",
        settings: dict[str, Any] = {},
        cards: list[PathLike] = [],
        random_seed: int = 42,
        n_events_per_subrun: int = 100000,
    ) -> None:
        # Before output ------------------------------------------------------ #
        # Check if the executable exists
        if (_executable := shutil.which(executable)) is not None:
            self._executable = Path(_executable).resolve()
            _mg5_dir = self._executable.parent.parent
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
        # Case 3: it's a model provided by Madgraph5 (i.e. models in mg5/models)
        elif (_model_file := _mg5_dir / f"models/{model}").exists():
            self._model = _model_file.resolve()
        # Otherwise, raise FileNotFoundError
        else:
            raise FileNotFoundError(f"Model {model} does not exist.")

        self._definitions = definitions
        self._processes = processes
        self._output = Path(output)

        # After output ------------------------------------------------------- #
        self.shower = shower
        self.detector = detector
        self.settings = settings
        self.cards = [Path(card) for card in cards]
        self.random_seed = random_seed
        self.settings["iseed"] = random_seed

        # Multi run
        # Assuming n_events_per_subrun is 100, (n_subruns x 100):
        # n_events = 10000 -> 10 x 100
        # n_events = 10001 -> 11 x 100
        # n_events = 10    -> 1 x 10
        n_events = self.settings.get("nevents", 10000)
        n_subruns, rest_runs = divmod(n_events, n_events_per_subrun)
        # n_events < n_events_per_subrun
        if n_subruns == 0 and rest_runs != 0:
            n_subruns = 1
            self.n_events_per_subrun = n_events
        # n_events > n_events_per_subrun
        elif n_subruns != 0 and rest_runs != 0:
            n_subruns += 1
            self.n_events_per_subrun = n_events_per_subrun
        self.n_subruns = n_subruns

        for card in self.cards:
            # Check if the card exists
            if not card.exists():
                raise FileNotFoundError(f"{card} does not exist.")

            # If it is a pythia8 card, set the random seed
            if card.name.startswith("pythia8"):
                with card.open() as f:
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
                        lines[i] = f"Random:seed = {random_seed}\n"

                if not set_seed:
                    lines.append("Random:setSeed = on\n")
                    lines.append(f"Random:seed = {random_seed}\n")
                elif not found_seed:
                    lines.append(f"Random:seed = {random_seed}\n")

                # Write back with the new random seed
                with card.open("w") as f:
                    f.writelines(lines)

            # If it is a delphes card, set the random seed
            elif card.name.startswith("delphes"):
                with card.open() as f:
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
                        lines[i] = f"set RandomSeed {random_seed}\n"
                        found_seed = True

                if not found_seed:
                    lines = [f"set RandomSeed {random_seed}\n"] + lines

                # Write back with the new random seed
                with card.open("w") as f:
                    f.writelines(lines)

    @property
    def executable(self) -> Path:
        """The executable file path of Madgraph5."""
        return self._executable

    @property
    def model(self) -> Path:
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
    def madevent_dir(self) -> Path:
        """The output directory of events."""
        all_dirs = [i for i in self.output.glob("madevent_*") if i.is_dir()]
        n_madevents = len(all_dirs)
        madevent_dir = self.output / f"madevent_{n_madevents + 1}"
        return madevent_dir

    def commands(self, new_output: bool = False) -> list[str]:
        """Commands converted from parameters to be executed in Madgraph5."""
        if new_output or not self.output.exists():
            shutil.rmtree(self.output, ignore_errors=True)
            self.output.mkdir(parents=True, exist_ok=True)

        settings = self.settings.copy()
        settings["nevents"] = self.n_events_per_subrun

        commands = [
            *[f"import model {self.model.absolute()}"],
            *[f"define {k} = {v}" for k, v in self.definitions.items()],
            *[f"generate {self.processes[0]}"],
            *[f"add process {p}" for p in self.processes[1:]],
            *[f"output {self.madevent_dir.absolute()}"],
            *[f"launch -i {self.madevent_dir.absolute()}"],
            *[f"multi_run {self.n_subruns}"],
            *[f"shower={self.shower}"],
            *[f"detector={self.detector}"],
            *[f"set {k} {v}" for k, v in settings.items()],
            *[f"{c.absolute()}" for c in self.cards],
            *[
                f"print_results"
                f" --path={self.madevent_dir.absolute()}/results.txt"
                f" --format=short"
            ],
        ]

        return commands

    @property
    def runs(self) -> list[MG5Run]:
        """Madgraph5 runs of all launches."""
        runs = [MG5Run(i) for i in sorted(self.output.glob("madevent_*")) if i.is_dir()]
        return runs

    def summary(self) -> None:
        """Summary of all runs."""
        console = Console()
        table = Table(
            title=f"Processes: {self.processes}",
            caption=f"Output: {self.output.absolute().relative_to(Path.cwd())}",
        )

        table.add_column("#", justify="right")
        table.add_column("Name (N subruns)")
        table.add_column("Tag")
        table.add_column("Cross section +- Error pb", justify="center")
        table.add_column("N events", justify="right")

        for i, run in enumerate(self.runs):
            table.add_row(
                f"{i}",
                f"{run.name} ({run.n_subruns})",
                f"{run.tag}",
                f"{run.cross_section:.5e} +- {run.error:.5e}",
                f"{run.n_events:,}",
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

        executable = shutil.which(self.executable)
        temp_file_path = self._commands_to_file(self.commands(new_output))

        # Launch Madgraph5 and redirect output to a log file
        log = self.madevent_dir.with_suffix(".log")
        with open(log, "w") as f:
            process = subprocess.Popen(
                f"{executable} {temp_file_path}",
                shell=True,
                stdout=f,
                stderr=subprocess.PIPE,
            )

        # Check and print status
        status = ""
        while (status != "Done") or process.poll() is None:
            # Madgraph5 generate py.py not only at the beginning but also the
            # middle of launching.
            if Path("py.py").exists():
                Path("py.py").unlink(missing_ok=True)

            last_status = self._check_status(log, status)
            if last_status != status:
                if show_status and last_status != "":
                    print(last_status)
                status = last_status
            if status == "Failed":
                stderr = process.stderr.readline().decode().strip()
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

    def _commands_to_file(self, commands: list[str]) -> str:
        """Write commands to a temporary file and return the path of the file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(commands))
            temp_file_path = temp_file.name
        return temp_file_path

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

        self._events = ROOT.TChain("Delphes")
        self._n_subruns = 0

        root_files = list((self.dir / "Events").glob("**/*.root"))
        if len(root_files) == 0:
            raise FileNotFoundError(f"No root file found in {self.dir}.")
        for file in root_files:
            self._n_subruns += 1
            self._events.Add(file.as_posix())

        # results.txt are updated each time a generator finishes running.
        # New run results are appended to the end of the file.
        # So we need to read the line that the run_name is exactly the same with
        # the run name of the instance.
        results = self.dir / "results.txt"
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
