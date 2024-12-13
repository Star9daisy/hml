import awkward as ak
import vector
from typeguard import typechecked

from .aliases import AwkwardArray, PathLike
from .builtins import Path

vector.register_awkward()


@typechecked
def path_like_to_path(path: PathLike) -> Path:
    return Path(path)


@typechecked
def momentum_to_array(momentum: AwkwardArray) -> AwkwardArray:
    return ak.with_name(momentum, None)


@typechecked
def array_to_momentum(array: AwkwardArray) -> AwkwardArray:
    return ak.with_name(array, "Momentum4D")


@typechecked
def pxpypze_to_ptetaphim(momentum: AwkwardArray) -> AwkwardArray:
    return ak.zip(
        {
            "pt": momentum.pt,
            "eta": momentum.eta,
            "phi": momentum.phi,
            "m": momentum.m,
        },
        with_name="Momentum4D",
    )
