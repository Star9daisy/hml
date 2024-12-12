import uproot

from ..types.aliases import PathLike, ROOTEvents
from ..types.utils import path_like_to_path


def load_events(path: PathLike) -> ROOTEvents:
    file = path_like_to_path(path)

    if file.suffix == ".root":
        return uproot.open(path)["Delphes"]  # type: ignore

    else:
        raise ValueError(f"Invalid path: {path}")
