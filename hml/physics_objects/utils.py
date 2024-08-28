import inflection
from typeguard import typechecked

from ..saving import retrieve
from .nested import Nested
from .single import Single


@typechecked
def parse_physics_object(name: str) -> Single | Nested:
    name = inflection.underscore(name)

    retrieved = retrieve(name)

    if retrieved is None:
        raise ValueError(f"Physics object {name} not found")

    return retrieved
