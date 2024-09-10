from functools import reduce

from typeguard import typechecked

from ..events import Events
from ..physics_objects import PhysicsObject
from ..saving import register
from ..types import AwkwardArray, array_to_momentum
from .observable import Observable


# ---------------------------------------------------------------------------- #
@typechecked
class InvM(Observable):
    def __init__(self, physics_object: list[PhysicsObject], **kwargs) -> None:
        super().__init__(physics_object, **kwargs)

    def get_array(self, events: Events) -> AwkwardArray:
        physics_objects = [obj.read(events) for obj in self.physics_object]
        arrays = [array_to_momentum(obj.array) for obj in physics_objects]
        summed = reduce(lambda x, y: x + y, arrays)
        return summed.mass


register(InvM, r"InvariantMass", exists_ok=True)
register(InvM, r"invariant_mass", exists_ok=True)
register(InvM, r"InvMass", exists_ok=True)
register(InvM, r"inv_mass", exists_ok=True)
register(InvM, r"InvM", exists_ok=True)
register(InvM, r"inv_m", exists_ok=True)
