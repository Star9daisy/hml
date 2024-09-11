from abc import ABC, abstractmethod
from typing import Self

import awkward as ak
import inflection
from typeguard import typechecked

from ..events import Events
from ..physics_objects import PhysicsObject, parse_physics_object
from ..types import AwkwardArray


@typechecked
class Observable(ABC):
    def __init__(
        self,
        physics_object: PhysicsObject | list[PhysicsObject] | None = None,
        name: str | None = None,
    ) -> None:
        self._physics_object = physics_object

        if name is not None:
            self._name = name

        classname = inflection.underscore(self.__class__.__name__)
        if physics_object is not None:
            objs = (
                physics_object if isinstance(physics_object, list) else [physics_object]
            )
            self._name = ",".join([obj.name for obj in objs]) + "." + classname
        else:
            self._name = classname

        self._array = ak.Array([])

    def __repr__(self) -> str:
        if self.array.typestr == "0 * unknown":
            return f"{self.name}: not read yet"

        return f"{self.name}: {self.array.typestr}"

    @property
    def physics_object(self) -> PhysicsObject | list[PhysicsObject] | None:
        return self._physics_object

    @property
    def name(self) -> str:
        return self._name

    @property
    def array(self) -> AwkwardArray:
        return self._array

    @abstractmethod
    def get_array(self, events: Events) -> AwkwardArray: ...

    def read(self, events: Events) -> Self:
        array = self.get_array(events)
        self._array = array
        return self

    @property
    def config(self) -> dict:
        config = {}

        if self.physics_object is None:
            config["physics_object"] = None
        if not isinstance(self.physics_object, list):
            config["physics_object"] = self.physics_object.name
        else:
            config["physics_object"] = [obj.name for obj in self.physics_object]

        config["name"] = self.name
        return config

    @classmethod
    def from_config(cls, config: dict) -> "Observable":
        physics_object = config["physics_object"]

        if physics_object is None:
            physics_object = None
        elif isinstance(physics_object, str):
            physics_object = parse_physics_object(physics_object)
        elif isinstance(physics_object, list):
            physics_object = [parse_physics_object(obj) for obj in physics_object]

        name = config.get("name")

        return cls(physics_object=physics_object, name=name)
