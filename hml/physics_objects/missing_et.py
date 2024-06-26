import re
from typing import Self

import inflection

from ..naming import str_to_index
from ..registration import register
from .physics_object import PhysicsObjectBase


class MissingET(PhysicsObjectBase):
    @classmethod
    def from_name(cls, name: str) -> Self:
        camel_case = cls.__name__
        snake_case = inflection.underscore(camel_case)
        lower_case = cls.__name__.lower()
        key_pattern = rf"({camel_case}|{lower_case}|{snake_case}|MET|met)"
        indices_pattern = r"(\d*:?\d*)"
        match = re.fullmatch(rf"{key_pattern}{indices_pattern}", name)
        key, indices = match.groups()
        indices = [str_to_index(indices)]

        return cls(key=key, indices=indices)


MET = MissingET


register(MissingET, "MissingET", existing_ok=True)
register(MissingET, "missinget", existing_ok=True)
register(MissingET, "missing_et", existing_ok=True)
register(MissingET, "MET", existing_ok=True)
register(MissingET, "met", existing_ok=True)
