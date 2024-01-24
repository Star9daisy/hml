from math import nan
from typing import Any

from ..physics_objects.collective import is_collective
from ..physics_objects.single import is_single
from .observable import Observable


class TransverseMomentum(Observable):
    def __init__(
        self,
        physics_object: str,
        name: str | None = None,
        value: Any = None,
        dtype: Any = None,
    ):
        supported_types = ["single", "collective", "nested"]
        super().__init__(physics_object, supported_types, name, value, dtype)

    def read(self, event):
        self.physics_object.read(event)
        self._value = []

        for obj in self.physics_object.objects:
            if is_single(self.physics_object):
                self._value.append(obj.P4().Pt())

            elif is_collective(self.physics_object):
                if obj is not None:
                    self._value.append(obj.P4().Pt())
                else:
                    self._value.append(nan)

            else:
                values = [sub.P4().Pt() if sub is not None else nan for sub in obj]
                self._value.append(values)

        return self


class Pt(TransverseMomentum):
    ...


TransverseMomentum.add_alias("transverse_momentum")
Pt.add_alias("pt", "pT", "PT")
