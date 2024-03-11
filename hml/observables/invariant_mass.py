from functools import reduce

import awkward as ak
import vector

from hml.physics_objects.physics_object import PhysicsObject

from .observable import Observable
from .observable_utils import branches_to_momentum4d

vector.register_awkward()


class InvariantMass(Observable):
    def __init__(
        self,
        physics_object: str | PhysicsObject,
        class_name: str | None = None,
    ) -> None:
        supported_objects = ["single", "multiple"]
        super().__init__(physics_object, class_name, supported_objects)

    def read(self, events):
        all_keys = {i.lower(): i for i in events.keys(full_paths=False)}

        momenta = []
        for obj in self.physics_object.all:
            momentum4d = branches_to_momentum4d(events, all_keys[obj.branch.lower()])
            padded_momentum4d = ak.pad_none(momentum4d[:, *obj.slices], 1)
            momenta.append(padded_momentum4d)

        total = reduce(lambda x, y: x + y, momenta)
        self._value = total.mass

        return self
