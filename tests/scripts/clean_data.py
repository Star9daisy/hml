import shutil
from pathlib import Path

TESTS_DIR = Path(__file__).parent.parent
DATA_DIR = TESTS_DIR / "data"

if len(list(TESTS_DIR.glob("py.py"))) > 0:
    Path("py.py").unlink()

print(f"Clean {DATA_DIR}\n")

dirs = ["bin", "Cards", "HTML", "lib", "Source", "SubProcesses"]
files = [
    "myprocid",
    "README",
    "madevent.tar.gz",
    "index.html",
    "README.systematics",
    "MGMEVersion.txt",
    "TemplateVersion.txt",
]
allowed_run_file_suffixes = [".gz", ".root", ".txt"]  # lhe, hepmc

for i, mg5_dir in enumerate(DATA_DIR.glob("*")):
    print(f"Check #{i} {mg5_dir}")
    for f in mg5_dir.glob("*"):
        if f.is_dir() and f.name in dirs:
            print(f"Remove {f.relative_to(DATA_DIR)}")
            shutil.rmtree(f, ignore_errors=True)
        elif f.is_file() and f.name in files:
            print(f"Remove {f.relative_to(DATA_DIR)}")
            f.unlink(missing_ok=True)
        else:
            print(f"Keep {f.relative_to(DATA_DIR)}")

    events_dir = mg5_dir / "Events"
    for run in events_dir.glob("*"):
        if not run.is_dir():
            continue
        for run_file in run.glob("*"):
            if run_file.suffix not in allowed_run_file_suffixes:
                print(f"Remove {run_file.relative_to(DATA_DIR)}")
                run_file.unlink(missing_ok=True)

    print()
