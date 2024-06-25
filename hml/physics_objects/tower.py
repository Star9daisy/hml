from typing import Self

import uproot

from ..events import DelphesEvent
from ..registration import register
from .physics_object import PhysicsObjectBase


class Tower(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        return super().read(events)


register(Tower, "Tower", existing_ok=True)
register(Tower, "tower", existing_ok=True)
