import inflection
from typeguard import typechecked

from ..saving import retrieve
from .physics_object import Nested, Single


@typechecked
def parse_physics_object(name: str) -> Single | Nested:
    name = inflection.underscore(name)
    return retrieve(name)
