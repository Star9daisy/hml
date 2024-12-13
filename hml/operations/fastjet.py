import awkward as ak
import fastjet as fj

from ..types import AwkwardArray


def get_algorithm(name: str) -> int:
    supported_algorithms = {
        "kt": fj.kt_algorithm,
        "ca": fj.cambridge_aachen_algorithm,
        "ak": fj.antikt_algorithm,
    }

    if name not in supported_algorithms:
        raise ValueError(f"Invalid name: {name}")
    else:
        return supported_algorithms[name]


def get_inclusive_jets(
    particles: AwkwardArray, algorithm: str, radius: float
) -> tuple[AwkwardArray, AwkwardArray]:
    definition = fj.JetDefinition(get_algorithm(algorithm), radius)
    cluster = fj.ClusterSequence(particles, definition)

    jets = cluster.inclusive_jets()
    constituents = cluster.constituents()

    sort_indices = ak.argsort(jets.pt, ascending=False)
    jets = jets[sort_indices]
    constituents = constituents[sort_indices]

    return jets, constituents  # type: ignore
