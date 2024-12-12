import awkward as ak
from typeguard import typechecked

from .aliases import AwkwardArray, PathLike
from .builtins import Path


@typechecked
def path_like_to_path(path: PathLike) -> Path:
    return Path(path)


@typechecked
def momentum_to_array(momentum: AwkwardArray) -> AwkwardArray:
    return ak.zip({i: momentum[i] for i in momentum.fields})


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
