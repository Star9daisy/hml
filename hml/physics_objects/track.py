from typing import Self

import uproot

from ..events import DelphesEvent
from .physics_object import PhysicsObjectBase


class Track(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        return super().read(events)
