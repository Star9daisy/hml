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
            self._model = self._executable.parent.parent / f"models/{model}"
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
        """The executable file path of Madgraph5."""
        return self._executable

    @property
    def output(self) -> Path:
        """The output directory of events."""
        return self._output

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

    @property
    def runs(self) -> list[MG5Run]:
        """Madgraph5 runs of all launches."""
        events_dir = self.output / "Events"
        run_dirs = events_dir.glob("run_*")
        run_dirs = [i for i in run_dirs if i.name.count("_") == 1]
        runs = [MG5Run(i) for i in sorted(run_dirs)]
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
        new_output:
            If True, remove the existing output directory and generate new
            events, else create a new run.
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

    def remove(self, run_name: str) -> None:
        """Remove one run."""
        paths = (self.output / "Events").glob(f"{run_name}*")
        run_dirs = [i for i in paths if i.is_dir()]
        banner_path = self.output / f"Events/{run_name}_banner.txt"

        commands = [
            f"launch -i {self.output.absolute()}",
            *[f"remove {i.name} all banner -f" for i in run_dirs],
        ]
        temp_file_path = self._commands_to_file(commands)
        subprocess.run(
            f"{self.executable} {temp_file_path}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        banner_path.unlink(missing_ok=True)

    def clean(self) -> None:
        """Remove the output directory."""
        shutil.rmtree(self.output, ignore_errors=True)
        self.output.with_suffix(".log").unlink(missing_ok=True)

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
        for file in self.dir.parent.glob(f"{self.dir.name}*/*.root"):
            self._n_subruns += 1
            self._events.Add(file.as_posix())

        # results.txt are updated each time a generator finishes running.
        # New run results are appended to the end of the file.
        # So we need to read the line that the run_name is exactly the same with
        # the run name of the instance.
        results = self.dir.parent.parent / "results.txt"
        info = []
        with open(results, "r") as f:
            for result in f:
                # When generating events using `multi_run 1`,
                # runs are:
                # - run_01
                # - run_01_0
                # Sometimes, the cross section of run_01 is not recorded, so
                # we need to resolve information from run_01_0.
                if self._n_subruns > 1:
                    query_name = self._name
                else:
                    query_name = self._name + "_0"

                # The first five columes in results.txt are:
                # run_name tag cross error Nb_event
                # In HML, they are renamed to: name, tag, cross_section, error,
                # n_events. As "name" is also the name of run directory (e.g.
                # the run_01 is the "run_name" and also the run directory), here
                # we only catch the four columns after run_name.
                if result.startswith(query_name):
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
    def events(self) -> TChain:
        """Events read by PyROOT of a run."""
        return self._events
