from typeguard import typechecked

from ..saving import retrieve
from .observable import Observable


@typechecked
def parse_observable(name: str) -> Observable:
    retrieved = retrieve(name)

    if retrieved is None:
        raise ValueError(f"Observable {name} not found")

    return retrieved
