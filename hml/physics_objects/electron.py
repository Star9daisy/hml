from typing import Self

import uproot

from ..events import DelphesEvent
from ..registration import register
from .physics_object import PhysicsObjectBase


class Electron(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        super().read(events)
        self._values["charge"] = self.events[f"{self.key.lower()}.charge"]
        return self


register(Electron, "Electron", existing_ok=True)
register(Electron, "electron", existing_ok=True)
