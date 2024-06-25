from typing import Self

import uproot

from ..events import DelphesEvent
from ..registration import register
from .physics_object import PhysicsObjectBase


class Track(PhysicsObjectBase):
    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        return super().read(events)


register(Track, "Track", existing_ok=True)
register(Track, "track", existing_ok=True)
