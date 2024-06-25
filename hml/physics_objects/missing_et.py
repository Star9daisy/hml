import re
from typing import Self

import uproot

from ..events import DelphesEvent
from ..naming import str_to_index
from ..registration import register
from .physics_object import PhysicsObjectBase


class MissingET(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        return super().read(events)

    @classmethod
    def from_name(cls, name: str) -> Self:
        key_pattern = rf"({cls.__name__}|{cls.__name__.lower()}|MET|met)"
        indices_pattern = r"(\d*:?\d*)"
        match = re.fullmatch(rf"{key_pattern}{indices_pattern}", name)
        key, indices = match.groups()
        indices = [str_to_index(indices)]

        return cls(key=key, indices=indices)


MET = MissingET


register(MissingET, "MissingET", existing_ok=True)
register(MissingET, "missing_et", existing_ok=True)
register(MissingET, "MET", existing_ok=True)
register(MissingET, "met", existing_ok=True)
