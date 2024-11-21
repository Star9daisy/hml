import awkward as ak
import vector
from typeguard import typechecked

from .aliases import Index
from .externals import AwkwardArray, MomentumArray

vector.register_awkward()


@typechecked
def array_to_momentum(array: AwkwardArray) -> MomentumArray:
    return ak.zip({i: array[i] for i in array.fields}, with_name="Momentum4D")


@typechecked
def momentum_to_array(momentum: MomentumArray) -> AwkwardArray:
    return ak.zip({i: momentum[i] for i in momentum.fields})


@typechecked
def pxpypze_to_ptetaphimass(momentum: MomentumArray) -> MomentumArray:
    return ak.zip(
        {
            "pt": momentum.pt,
            "eta": momentum.eta,
            "phi": momentum.phi,
            "mass": momentum.mass,
        },
        with_name="Momentum4D",
    )


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
