from typing import Self

import uproot

from ..events import DelphesEvent
from ..registration import register
from .physics_object import PhysicsObjectBase


class Muon(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        super().read(events)
        self._values["charge"] = self.events[f"{self.key.lower()}.charge"]
        return self


register(Muon, "Muon", existing_ok=True)
register(Muon, "muon", existing_ok=True)
