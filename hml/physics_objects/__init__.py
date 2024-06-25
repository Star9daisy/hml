from ..registration import (
    deserialize,
    is_registered,
    retrieve,
    search_registered_classes,
)
from ..types import PhysicsObject
from .electron import Electron
from .jet import Jet
from .missing_et import MET, MissingET
from .muon import Muon
from .photon import Photon
from .physics_object import PhysicsObjectBase
from .tower import Tower
from .track import Track


def parse_physics_object(name: str) -> PhysicsObject:
    """Parse a physics object from its name."""
    if is_registered(name):
        obj = retrieve(name)

    else:
        item = search_registered_classes(name)
        obj = deserialize(item["serialized_obj"])

    if isinstance(obj, type):
        return obj.from_name(name)
    else:
        return obj
