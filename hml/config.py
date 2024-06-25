from pathlib import Path

HOME_DIR = Path().home() / ".hml"
REGISTRY_PATH = HOME_DIR / "registry.json"


if not HOME_DIR.exists():
    HOME_DIR.mkdir()


def get_home_dir() -> Path:
    """Set the home directory for hml."""
    return HOME_DIR


def set_home_dir(dir) -> None:
    """Set the home directory for hml."""
    global HOME_DIR
    HOME_DIR = Path(dir)
