from typeguard import typechecked

from .aliases import PathLike
from .builtins import Path


@typechecked
def path_like_to_path(path: PathLike) -> Path:
    return Path(path)
