import awkward as ak
import fastjet as fj

from ..types import AwkwardArray, MomentumArray


def get_jet_algorithm(name: str) -> int:
    if name == "kt":
        return fj.kt_algorithm
    elif name == "ca":
        return fj.cambridge_algorithm
    elif name == "ak":
        return fj.antikt_algorithm
    else:
        raise ValueError(f"{name} is not supported yet")


def get_inclusive_jets(
    particles: AwkwardArray,
    algorithm: str,
    radius: float,
    return_constituents: bool = False,
) -> MomentumArray | tuple[MomentumArray, MomentumArray]:

    definition = fj.JetDefinition(get_jet_algorithm(algorithm), radius)
    cluster = fj.ClusterSequence(particles, definition)

    jets = cluster.inclusive_jets()
    constituents = cluster.constituents()

    sort_indices = ak.argsort(jets.pt, ascending=False)
    jets = jets[sort_indices]
    constituents = constituents[sort_indices]

    if not return_constituents:
        return jets

    return jets, constituents
