from functools import reduce

import numpy as np
from typeguard import typechecked

from ..events import Events
from ..physics_objects import PhysicsObject
from ..saving import registered_object
from ..types import AwkwardArray, array_to_momentum
from .observable import Observable


@typechecked
@registered_object(r"(?P<physics_object>[\w:._]+)\.(InvariantMass|invariant_mass)")
@registered_object(r"(?P<physics_object>[\w:._]+)\.(InvMass|inv_mass|InvM|inv_m)")
class InvM(Observable):
    def __init__(self, physics_object: list[PhysicsObject], **kwargs) -> None:
        super().__init__(physics_object, **kwargs)

    def get_array(self, events: Events) -> AwkwardArray:
        objs = [obj.read(events) for obj in self.physics_object]

        if np.unique([obj.array.ndim for obj in objs]).size > 1:
            raise ValueError("ndim mismatch")

        if np.unique([obj.array.typestr.split(" * ")[1:-1] for obj in objs]).size > 1:
            raise ValueError("type mismatch")

        momenta = [array_to_momentum(obj.array) for obj in objs]
        summed = reduce(lambda x, y: x + y, momenta)
        return summed.mass
