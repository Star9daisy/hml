import re
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal, Self

import pexpect
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from typeguard import typechecked

from ..types import PathLike, pathlike_to_path


@typechecked
class Madgraph5Run:
    def __init__(self, output_dir: PathLike, name: str):
        self.output_dir = pathlike_to_path(output_dir)
        self._events_dir = self.output_dir / "Events"
        self._run_dir = self._events_dir / name

        self._info = self._get_info(output_dir, name)
        self._subs = []
        for i in self._events_dir.glob(f"{name}_*"):
            if i.is_dir():
                self._subs.append(i)

    @property
    def directory(self) -> Path:
        return self._run_dir

    @property
    def name(self) -> str:
        return self._info["name"]

    @property
    def collider(self) -> str:
        return self._info["collider"]

    @property
    def tag(self) -> str:
        return self._info["tag"]

    @property
    def seed(self) -> int:
        return self._info["seed"]

    @property
    def cross(self) -> float:
        return self._info["cross"]

    @property
    def error(self) -> float:
        return self._info["error"]

    @property
    def n_events(self) -> int:
        return self._info["n_events"]

    @property
    def sub_runs(self) -> list[Self]:
        return [Madgraph5Run(self.output_dir, i.name) for i in self._subs]

    def event_paths(self) -> dict[str, list[Path]]:
        lhe_files = list(self.directory.parent.glob(f"{self.name}*/*.lhe"))
        hepmc_files = list(self.directory.parent.glob(f"{self.name}*/*.hepmc"))
        root_files = list(self.directory.parent.glob(f"{self.name}*/*.root"))

        return {"lhe": lhe_files, "hepmc": hepmc_files, "root": root_files}

    def __repr__(self) -> str:
        head = self.name
        if self.sub_runs != []:
            head += f" ({len(self.sub_runs)} sub runs)"
        return (
            f"Madgraph5Run {head}:\n"
            f"- collider: {self.collider}\n"
            f"- tag: {self.tag}\n"
            f"- seed: {self.seed}\n"
            f"- cross: {self.cross}\n"
            f"- error: {self.error}\n"
            f"- n_events: {self.n_events}"
        )

    def _get_info(self, output_dir: str | Path, name: str):
        output_dir = Path(output_dir)
        events_dir = output_dir / "Events"
        run_dir = events_dir / name

        if list(run_dir.glob("*_banner.txt")) != []:
            banner_file = list(run_dir.glob("*_banner.txt"))[0]
        elif list(events_dir.glob(f"{name}_banner.txt")) != []:
            banner_file = list(events_dir.glob(f"{name}_banner.txt"))[0]
        else:
            raise FileNotFoundError("Banner file not found")

        crossx_file = output_dir / "crossx.html"

        with crossx_file.open() as f:
            soup = BeautifulSoup(f, "html.parser")

        table = soup.find("table")
        run = {}
        for row in table.find_all("tr")[1:]:  # type: ignore
            columns = row.find_all("td")
            if columns[0].text != name:
                continue

            # Name
            run["name"] = name

            # Collider
            collider_col = columns[1].text.split()
            lpp1, lpp2 = collider_col[:2]
            ebeam1, ebeam2 = collider_col[2], collider_col[4]
            run["collider"] = f"{lpp1}{lpp2}:{ebeam1}x{ebeam2}"

            # Banner
            banner_col = columns[2].text.split()
            run["tag"] = banner_col[0]

            with banner_file.open() as f:
                for line in f.readlines():
                    if "iseed" in line:
                        run["seed"] = int(line.split("=")[0].strip())
                        break

            # Cross section and error
            cross_col = columns[3].text.split()
            cross = float(cross_col[0])
            error = float(cross_col[2])
            run["cross"] = cross
            run["error"] = error

            # N Events
            events_col = columns[4].text.split()
            run["n_events"] = int(events_col[0])

            # ROOT file path
            run["events"] = {}
            if list(run_dir.glob("*lhe*")) != []:
                run["events"]["lhe"] = list(run_dir.glob("*lhe*"))[0].as_posix()
            if list(run_dir.glob("*hepmc*")) != []:
                run["events"]["hepmc"] = list(run_dir.glob("*hepmc*"))[0].as_posix()
            if list(run_dir.glob("*.root")) != []:
                run["events"]["root"] = list(run_dir.glob("*.root"))[0].as_posix()

        return run


@typechecked
class Madgraph5:
    def __init__(self, executable: PathLike | None = None, verbose: int = 1):
        if executable is None:
            self.executable = executable
        else:
            self.executable = shutil.which(pathlike_to_path(executable))

        self.verbose = verbose
        self._spawn_process()

    def _spawn_process(self):
        # Init attributes
        self.child = None
        self.version = None
        self.model = None
        self.model_dir = None
        self.multi_particles = {}

        # Check if the executable is available
        if self.executable is None:
            return

        # Spawn the process
        self.child = pexpect.spawn(
            self.executable, timeout=None, echo=False, encoding="utf-8"
        )

        # Loop over the output
        while self.child.expect([r"\n", r"MG5_aMC>$"]) == 0:
            output = self.child.before.rstrip() + self.child.after.rstrip()

            if match := re.search(r"VERSION ([\d\.]+)", output):
                self.version = match.group(1)

                if self.verbose == 1:
                    print(f"MadGraph5_aMC@NLO v{self.version}")

            if output.startswith("Loading default model"):
                self.model = output.split(" ")[-1]

            if match := re.search(r"with file (.*)/", output):
                self.model_dir = match.group(1)

            if output.startswith("Defined multiparticle"):
                name = output.split(" = ")[0].split(" ")[-1]
                particles = output.split(" = ")[1]
                self.multi_particles[name] = particles

            elif self.verbose == 2:
                print(output)

        # Clean the pypy file
        self._clean_pypy_file()

    def _clean_pypy_file(self):
        py_py = Path("py.py")

        if py_py.exists():
            py_py.unlink()

    def import_model(self, model: PathLike) -> None:
        # Init attributes
        self.model = model
        self.model_dir = None

        # Send commands
        self.child.sendline(f"import model {model}")

        # Init error handling
        error_message = []
        has_error = False

        # Loop over the output
        while self.child.expect([r"\n", r"MG5_aMC>$"]) == 0:
            output = self.child.before.rstrip() + self.child.after.rstrip()

            if re.search(r"\x1b\[1;31m", output) or has_error:
                has_error = True
                error_message.append(output)

            if match := re.search(r"with file (.*)/", output):
                self.model_dir = match.group(1)

                if self.verbose == 1:
                    print(f"Imported {self.model_dir}")

            elif self.verbose == 2:
                print(output)

        # Clean the pypy file
        self._clean_pypy_file()

        # Raise error if any
        if has_error:
            print("\n".join(error_message)) if self.verbose != 2 else None
            raise ValueError(f"Error importing model {model!r}")

    def define(self, multi_particles: dict[str, str]) -> None:
        # No need to init attributes
        # It's done in _spawn_process

        # Loop over the multi-particles to send commands
        for name, particles in multi_particles.items():
            self.child.sendline(f"define {name} = {particles}")

            # Init error handling
            error_message = []
            has_error = False

            # Loop over the output
            while self.child.expect([r"\n", r"MG5_aMC>$"]) == 0:
                output = self.child.before.rstrip() + self.child.after.rstrip()

                if re.search(r"\x1b\[1;31m", output) or has_error:
                    has_error = True
                    error_message.append(output)

                if output.startswith("Defined"):
                    self.multi_particles[name] = particles

                    if self.verbose == 1:
                        print(f"Defined {name} = {particles}")

                if self.verbose == 2:
                    print(output)

            # Clean the pypy file
            self._clean_pypy_file()

            # Raise error if any
            if has_error:
                print("\n".join(error_message)) if self.verbose != 2 else None
                raise ValueError(f"Error defining {name!r}")

    def generate(self, processes: list[str]) -> None:
        # Init attributes
        self.processes = processes

        # Loop over the processes to send commands
        for i, process in enumerate(processes):
            if i == 0:
                self.child.sendline(f"generate {process}")
            else:
                self.child.sendline(f"add process {process}")

            # Init error handling
            error_message = []
            has_error = False

            # Loop over the output
            while self.child.expect([r"\n", r"MG5_aMC>$"]) == 0:
                output = self.child.before.rstrip() + self.child.after.rstrip()

                if re.search(r"\x1b\[1;31m", output) or has_error:
                    has_error = True
                    error_message.append(output)

                if self.verbose == 1 and output.startswith("Total: "):
                    print(output)

                elif self.verbose == 2:
                    print(output)

            # Clean the pypy file
            self._clean_pypy_file()

            # Raise error if any
            if has_error:
                print("\n".join(error_message)) if self.verbose != 2 else None
                raise ValueError(f"Error generating {process!r}")

    def display_diagrams(
        self,
        diagrams_dir: PathLike = Path("Diagrams"),
        overwrite: bool = True,
        convert_to_pdf: bool = True,
        clean_eps: bool = True,
    ) -> None:
        # Init attributes
        self.diagrams_dir = pathlike_to_path(diagrams_dir).resolve()

        # Check if the directory exists
        if self.diagrams_dir.exists():
            if overwrite:
                shutil.rmtree(self.diagrams_dir)
            else:
                raise FileExistsError(f"Directory {self.diagrams_dir} already exists.")

        # Create the directory
        self.diagrams_dir.mkdir(parents=True)

        # Send command
        self.child.sendline(f"display diagrams {self.diagrams_dir.as_posix()}")

        # Loop over the output
        while self.child.expect([r"\n", r"MG5_aMC>$"]) == 0:
            output = self.child.before.rstrip() + self.child.after.rstrip()

            if self.verbose == 2:
                print(output)

        # Clean the pypy file
        self._clean_pypy_file()

        # Convert to pdf and clean the eps files if requested
        n_diagrams = 0
        if convert_to_pdf:
            for eps in self.diagrams_dir.glob("*.eps"):
                subprocess.run(f"ps2pdf {eps} {eps.with_suffix('.pdf')}", shell=True)
                eps.unlink() if clean_eps else None
                n_diagrams += 1

        # Print the number of diagrams
        if self.verbose == 1:
            print(f"Saved {n_diagrams} diagrams in {self.diagrams_dir}")

    def output(
        self, output_dir: PathLike | None = None, overwrite: bool = True
    ) -> None:
        # Init attributes
        self.output_dir = None

        if output_dir is not None:
            output_dir = pathlike_to_path(output_dir)

            # Check if the directory exists
            if output_dir.exists():
                if overwrite:
                    shutil.rmtree(output_dir)
                else:
                    raise FileExistsError(f"Directory {output_dir!s} already exists.")

        # Send command
        if output_dir is None:
            self.child.sendline("output")
        else:
            # -f: force cleaning of the directory if it already exists
            self.child.sendline(f"output {output_dir.as_posix()} -f")

        # Loop over the output
        while self.child.expect([r"\n", r"MG5_aMC>$"]) == 0:
            output = self.child.before.rstrip() + self.child.after.rstrip()

            if match := re.search(r"Output to directory (.*) done\.", output):
                self.output_dir = Path(match.group(1))

                if self.verbose == 1:
                    print(f"Output to {self.output_dir}")

            elif self.verbose == 2:
                print(output)

        # Clean the pypy file
        self._clean_pypy_file()

    def launch(
        self,
        shower: Literal["off", "pythia8"] = "off",
        detector: Literal["off", "delphes"] = "off",
        madspin: Literal["off", "on"] = "off",
        settings: dict | None = None,
        decays: list[str] | None = None,
        cards: dict | None = None,
        multi_run: int = 1,
        seed: int | None = None,
        dry_run: bool = False,
    ):
        # Init attributes
        settings = {} if settings is None else settings
        decays = [] if decays is None else decays
        cards = {} if cards is None else cards
        seed = 0 if seed is None else seed

        # Build commands
        commands = [
            f"launch -i {self.output_dir}",
            "generate_events" if multi_run == 1 else f"multi_run {multi_run}",
            f"shower={shower}",
            f"detector={detector}",
            f"madspin={madspin}",
            "done",
        ]

        # Settings
        if "iseed" not in settings and seed != 0:
            settings["iseed"] = seed

        commands += [f"set {key} {value}" for key, value in settings.items()]

        # Decays
        commands += [f"decay {decay}" for decay in decays]

        # Parse pythia8 and delphes cards
        default_pythia8_card = self.output_dir / "Cards/pythia8_card_default.dat"
        default_delphes_card = self.output_dir / "Cards/delphes_card_default.dat"
        resolved_cards = {}

        if shower == "pythia8" or detector == "delphes":
            pythia8_card = cards.get("pythia8", default_pythia8_card)
            pythia8_card = pathlike_to_path(pythia8_card)

            with pythia8_card.open("r") as f:
                lines = f.readlines()
                set_seed = False
                found_seed = False
                for i, line in enumerate(lines):
                    if line.startswith("Random:setSeed = on"):
                        set_seed = True
                    if line.startswith("Random:seed"):
                        found_seed = True
                        lines[i] = f"Random:seed = {seed}\n"
                        break

                if not set_seed:
                    lines.append("Random:setSeed = on\n")
                    lines.append(f"Random:seed = {seed}\n")
                elif not found_seed:
                    lines.append(f"Random:seed = {seed}\n")

            with NamedTemporaryFile(delete=False, prefix="pythia8_card_") as temp:
                temp.write("".join(lines).encode())

            resolved_cards["pythia8"] = temp.name

        if detector == "delphes":
            delphes_card = cards.get("delphes", default_delphes_card)
            delphes_card = pathlike_to_path(delphes_card)

            with delphes_card.open("r") as f:
                lines = f.readlines()
                found_seed = False
                for i, line in enumerate(lines):
                    if line.startswith("set RandomSeed"):
                        found_seed = True
                        lines[i] = f"set RandomSeed {seed}\n"
                        break

                if not found_seed:
                    lines.insert(0, f"set RandomSeed {seed}\n")

            with NamedTemporaryFile(delete=False, prefix="delphes_card_") as temp:
                temp.write("".join(lines).encode())

            resolved_cards["delphes"] = temp.name

        commands += resolved_cards.values()
        commands += ["done"]

        # Return commands if dry run
        if dry_run:
            return commands

        # Send commands
        for command in commands:
            self.child.sendline(command)

        # Loop over the output
        while self.child.expect([r"\n", r">$"]) == 0:
            output = self.child.before.rstrip() + self.child.after.rstrip()

            if self.verbose == 1:
                if output.startswith("Generating"):
                    run_name = output.split(" ")[-1]
                    print(run_name + "...", end="")

                elif "Running Survey" in output:
                    print("survey...", end="")

                elif "Running Pythia8" in output:
                    print("pythia8...", end="")

                elif "Running Delphes" in output:
                    print("delphes...", end="")

                elif "storing files" in output:
                    print("storing...", end="")

                elif "INFO: Done" in output:
                    print("done")

            elif self.verbose == 2:
                print(output)

        # Quit MadEvent CLI
        self.child.sendline("quit")
        self.child.expect(r"MG5_aMC>$")

        # Clean the pypy file
        self._clean_pypy_file()

    @property
    def runs(self) -> list[Madgraph5Run]:
        run_paths = []
        for i in self.output_dir.glob("Events/run_*"):
            if i.is_dir() and i.name.count("_") == 1:
                run_paths.append(i)

        # Sort the runs by their number
        run_paths = sorted(run_paths, key=lambda x: int(x.name.split("_")[-1]))
        runs = [Madgraph5Run(self.output_dir, i.name) for i in run_paths]

        return runs

    def summary(self):
        console = Console()

        if self.output_dir.is_relative_to(Path.cwd()):
            output_dir = self.output_dir.relative_to(Path.cwd())
        else:
            output_dir = self.output_dir

        title = f"Results in the {self.model} for {', '.join(self.processes)}"
        table = Table(title=title, caption=f"Output: {output_dir}")

        table.add_column("#", justify="right")
        table.add_column("Name")
        table.add_column("Collider")
        table.add_column("Tag")
        table.add_column("Cross section (pb)", justify="center")
        table.add_column("N events", justify="right")
        table.add_column("Seed", justify="right")

        for i, run in enumerate(self.runs):
            table.add_row(
                f"{i}",
                f"{run.name}[{len(run.sub_runs)}]",
                f"{run.collider}",
                f"{run.tag}",
                f"{run.cross:.3e} +- {run.error:.3e}",
                f"{run.n_events:,}",
                f"{run.seed}",
            )

        console.print(table)

    @classmethod
    def from_output(
        cls,
        output_dir: PathLike,
        executable: PathLike | None = None,
        verbose: int = 1,
    ) -> Self:
        output_dir = pathlike_to_path(output_dir)
        if not output_dir.exists():
            raise FileNotFoundError(f"Output directory {output_dir} does not exist")

        # Parse the crossx.html file
        with (output_dir / "crossx.html").open() as f:
            soup = BeautifulSoup(f, "html.parser")
            title_column = soup.find_all("h2")[0].text.strip()
            match = re.match(r"^Results in the (.+) for (.+)", title_column)
            model, process = match.groups()
            processes = process.split(",")

        generator = cls(executable, verbose)

        # attributes in import_model
        # no self.model_dir
        generator.model = model

        # attributes in define
        # no self.definitions

        # attributes in generate
        generator.processes = processes

        # attributes in display_diagrams
        # no self.diagrams_dir

        # attributes in output
        generator.output_dir = output_dir

        return generator
