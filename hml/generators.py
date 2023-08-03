from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Union

import cppyy
import ROOT
from rich.console import Console
from rich.table import Table

ROOT.gSystem.Load("libDelphes")

PathLike = Union[str, Path, os.PathLike]


class Madgraph5:
    """Wrapper of Madgraph5 CLI to simulate colliding events.

    Madgraph5 is a wrapper class of Madgraph5 CLI. It mainly provides functionalities to generate
    events, run parton shower and detector simulation, and access to the launched runs.

    Parameters
    ----------
    executable:
        The executable file of Madgraph5.
    processes:
        The processes to be generated.
    output_dir:
        The directory where the events will be outputted.
    model:
        The particle physics model to be used.
    definitions:
        The definitions of multiparticle.
    shower:
        The parton shower tool to be used.
    detector:
        The detector simulation tool to be used.
    settings:
        The phase space and parameter settings.
    cards:
        Shower and detector configuration cards.

    Parameters correspond to commands in Madgraph5 CLI or options after launching generation in
    Madgraph5.

    | Parameters  | Madgraph5 commands or options    |
    |-------------|----------------------------------|
    | processes   | generate & add process commands  |
    | output_dir  | output command                   |
    | model       | import model command             |
    | definitions | define command                   |
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
        n_events_per_subrun: int = 100000,
    ) -> None:
        # Data validation ---------------------------------------------------- #
        _executable = shutil.which(executable)
        if _executable is None:
            raise EnvironmentError(f"{executable} does not exist.")
        self._executable = Path(_executable).resolve()

        self._output = Path(output)

        if Path(model).exists():
            self._model = Path(model)
        elif (self._executable.parent.parent / f"models/{model}").exists():
            self._model = model
        else:
            raise FileNotFoundError(f"Model {model} does not exist.")

        self._definitions = definitions
        self._processes = processes
        self.shower = shower
        self.detector = detector
        self.settings = settings
        self.cards = [Path(card) for card in cards]
        for card in self.cards:
            if not card.exists():
                raise FileNotFoundError(f"{card} does not exist.")
        self.n_events_per_subrun = n_events_per_subrun

    @property
    def executable(self) -> Path:
        """The executable file of Madgraph5."""
        return self._executable

    @property
    def output(self) -> Path:
        """The directory where all generation information is stored."""
        return self._output

    @property
    def model(self) -> PathLike:
        """The particle physics theory model to be used."""
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
    def commands(self) -> list[str]:
        """Commands converted from parameters to be executed in Madgraph5."""
        commands = []
        if not self.output.exists():
            # Model
            commands += [f"import model {str(self.model)}"]

            # Definitions
            commands += [f"define {k} = {v}" for k, v in self.definitions.items()]

            # Processes
            commands += [
                f"generate {process}" if i == 0 else f"add process {process}"
                for i, process in enumerate(self.processes)
            ]

            # Output
            commands += [f"output {self.output.absolute()}"]

        # Launch
        commands += [f"launch -i {self.output.absolute()}"]

        # Multi run
        # Assuming n_events_per_subrun is 100, (n_subruns x 100):
        # n_events = 10000 -> 10 x 100
        # n_events = 10001 -> 11 x 100
        # n_events = 10    -> 1 x 10
        n_events = self.settings.get("nevents", 10000)
        n_subruns, rest_runs = divmod(n_events, self.n_events_per_subrun)
        # n_events < n_events_per_subrun
        if n_subruns == 0 and rest_runs != 0:
            n_subruns = 1
            self.n_events_per_subrun = n_events
        # n_events > n_events_per_subrun
        elif n_subruns != 0 and rest_runs != 0:
            n_subruns += 1
        commands += [f"multi_run {n_subruns}"]

        # Shower
        commands += [f"shower={self.shower}"]

        # Detector
        commands += [f"detector={self.detector}"]

        # Settings
        commands += [
            f"set {k} {self.n_events_per_subrun}" if k == "nevents" else f"set {k} {v}"
            for k, v in self.settings.items()
        ]

        # Cards
        commands += [f"{c.absolute()}" for c in self.cards]

        # Print results
        commands += [
            f"print_results"
            f" --path={self.output.absolute()}/results.txt"
            f" --format=short"
        ]

        return commands

    @commands.setter
    def commands(self, new_commands: list[str]) -> list[str]:
        return new_commands

    @property
    def runs(self) -> list[MG5Run]:
        """Madgraph5 runs after finishing event generation."""
        events_dir = self.output / "Events"
        run_dirs = events_dir.glob("run_*")
        run_dirs = [i for i in run_dirs if i.name.count("_") == 1]
        runs = [MG5Run(i) for i in sorted(run_dirs)]
        return runs

    def summary(self) -> None:
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
        new_output:
            If True, remove the existing output directory and generate new events, else create a new
            run.
        show_status:
            If True, print the status of the launched run, else launch silently.
        """

        executable = shutil.which(self.executable)

        if new_output and self.output.exists():
            shutil.rmtree(self.output)

        temp_file_path = self._commands_to_file(self.commands)

        # Launch Madgraph5 and redirect output to a log file
        with open(f"{self.output}.log", "w") as f:
            process = subprocess.Popen(
                f"{executable} {temp_file_path}",
                shell=True,
                stdout=f,
                stderr=subprocess.PIPE,
            )

        # Check and print status
        status = ""
        while (status != "Done") or process.poll() is None:
            last_status = self._check_status(status)
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

        # Remove py.py file
        if Path("py.py").exists():
            Path("py.py").unlink()

    def _commands_to_file(self, commands: list[str]) -> str:
        """Write commands to a temporary file and return the path of the file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(commands))
            temp_file_path = temp_file.name
        return temp_file_path

    def _check_status(self, current_status: str) -> str:
        """Check the status of the launched run."""
        with open(f"{self.output}.log", "r") as f:
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


@dataclass
class MG5Run:
    """MG5Run stores the information of a Madgraph5 run.

    Parameters
    ----------
    directory: str | Path
        The directory path to a run.

    Attributes
    ----------
    directory: Path
        The directory path to a run.
    banner: Path
        The path to the banner file of a run.
    tag: str
        The tag of a run.
    cross_section: float
        The cross section of a run.
    n_events: int
        The number of events generated in a run.
    n_subruns: int
        The number of subruns in a run.
    events: TCahin
        The events generated in a run.
    """

    def __init__(self, dir: PathLike):
        _dir = Path(dir)
        if not _dir.exists():
            raise FileNotFoundError(f"Directory {_dir} does not exist.")
        self._dir = _dir
        self._name = _dir.name

        self._events = ROOT.TChain("Delphes")
        self._n_subruns = 0
        for file in self.dir.parent.glob(f"{self.dir.name}*/*.root"):
            self._n_subruns += 1
            self._events.Add(file.as_posix())

        results = self.dir.parent.parent / "results.txt"
        with open(results, "r") as f:
            for line in f:
                query_name = self._name if self._n_subruns > 1 else self._name + "_0"
                if line.startswith(query_name):
                    result = line.split()
                    break

        self._tag = result[1]
        self._cross_section = float(result[2])
        self._error = float(result[3])
        self._n_events = int(result[4])

    @property
    def dir(self) -> Path:
        return self._dir

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def cross_section(self) -> float:
        return self._cross_section

    @property
    def error(self) -> float:
        return self._error

    @property
    def n_events(self) -> int:
        return self._n_events

    @property
    def n_subruns(self) -> int:
        return self._n_subruns

    @property
    def events(self) -> TChain:
        return self._events
