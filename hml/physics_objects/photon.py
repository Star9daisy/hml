from typing import Self

import uproot

from ..events import DelphesEvent
from ..registration import register
from .physics_object import PhysicsObjectBase


class Photon(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        return super().read(events)


register(Photon, "Photon", existing_ok=True)
register(Photon, "photon", existing_ok=True)
