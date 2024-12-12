import uproot
from typeguard import typechecked

from ..types.aliases import PathLike, ROOTEvents
from ..types.utils import path_like_to_path


@typechecked
def load_events(path: PathLike) -> ROOTEvents:
    file = path_like_to_path(path)

    if file.suffix == ".root":
        return uproot.open(path)["Delphes"]  # type: ignore

    else:
        raise ValueError(f"Invalid path: {path}")
