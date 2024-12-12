import uproot

from ..types.aliases import PathLike, ROOTEvents


def load_events(path: PathLike) -> ROOTEvents:
    return uproot.open(path)["Delphes"]  # type: ignore
