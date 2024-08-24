from typeguard import typechecked

from ..types import PathLike, pathlike_to_path
from .events import Events
from .root_events import ROOTEvents


@typechecked
def load_events(file_path: PathLike) -> Events:
    """Load events from a file."""
    file_path = pathlike_to_path(file_path)

    match file_path.suffix:
        case ".root":
            return ROOTEvents.load(file_path)
        case _:
            raise ValueError(f"File type '{file_path.suffix}' not supported yet.")
