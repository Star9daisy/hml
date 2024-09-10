from typeguard import typechecked

from hml.physics_objects.physics_object import PhysicsObject

from ..events import Events
from ..saving import registered_object
from ..types import AwkwardArray
from .observable import Observable


@typechecked
@registered_object(r"(?P<physics_object>[\w:._]+)\.[Mm](?:ass)?")
class M(Observable):
    def __init__(
        self,
        physics_object: str | PhysicsObject,
        name: str | None = None,
    ) -> None:
        super().__init__(physics_object, name)

    def get_array(self, events: Events) -> AwkwardArray:
        self.physics_object.read(events)
        return self.physics_object.array.mass
