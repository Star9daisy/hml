from pathlib import Path

import awkward as ak
import vector
from typeguard import typechecked

from .aliases import AwkwardArray, Index, PathLike
from .externals import MomentumArray

vector.register_awkward()


@typechecked
def pathlike_to_path(path: PathLike) -> Path:
    """Convert a path-like object to a Path object."""
    if isinstance(path, str):
        path = Path(path)

    return path


@typechecked
def index_to_str(index: Index) -> str:
    """Convert an index to a string representation."""
    if isinstance(index, int):
        return str(index)

    match (index.start, index.stop):
        case (None, None):
            return ""
        case (None, stop):
            return f":{stop}"
        case (start, None):
            return f"{start}:"
        case (start, stop):
            return f"{start}:{stop}"


@typechecked
def str_to_index(string: str) -> Index:
    """Convert a string representation to an index."""
    if ":" not in string:
        index = int(string) if string != "" else slice(None)

    match string.split(":"):
        case ["", ""]:
            index = slice(None)
        case ["", stop]:
            index = slice(None, int(stop))
        case [start, ""]:
            index = slice(int(start), None)
        case [start, stop]:
            index = slice(int(start), int(stop))

    return index


@typechecked
def array_to_momentum(array: AwkwardArray) -> MomentumArray:
    """Convert an awkward array to a momentum array."""
    # Build a new array to avoid jaggedness issues
    # array = ak.from_iter(array)

    momentum = ak.zip({i: array[i] for i in array.fields}, with_name="Momentum4D")
    momentum = ak.values_astype(momentum, "float32")

    return momentum
