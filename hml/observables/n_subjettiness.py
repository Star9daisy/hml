from typing import Self

from typeguard import typechecked

from hml.physics_objects.physics_object import PhysicsObject

from ..events import Events
from ..saving import registered_object
from ..types import AwkwardArray
from .observable import Observable


@registered_object(r"(?P<physics_object>[\w:._]+)\.[Tt]au(?P<n>\d)")
class TauN(Observable):
    def __init__(
        self,
        n: int,
        physics_object: str | PhysicsObject,
        name: str | None = None,
    ) -> None:
        super().__init__(physics_object, name)
        self.n = n

    @property
    def name(self) -> str:
        if self._name:
            return self._name

        return f"tau{self.n}"

    def get_array(self, events: Events) -> AwkwardArray:
        self.physics_object.read(events)
        return self.physics_object.array[f"tau{self.n}"]

    @property
    def config(self) -> dict:
        config = super().config
        config["n"] = self.n
        return config

    @classmethod
    def from_config(cls, config: dict) -> Self:
        n = int(config["n"])
        name = config.get("name")
        return cls(n=n, physics_object=config["physics_object"], name=name)


@typechecked
@registered_object(r"(?P<physics_object>[\w:._]+)\.[Tt]au(?P<m>\d)(?P<n>\d)")
class TauMN(Observable):
    def __init__(
        self,
        m: int,
        n: int,
        physics_object: str | PhysicsObject,
        name: str | None = None,
    ) -> None:
        super().__init__(physics_object, name)
        self.m = m
        self.n = n

    @property
    def name(self) -> str:
        if self._name:
            return self._name

        return f"tau{self.m}{self.n}"

    def get_array(self, events: Events) -> AwkwardArray:
        self.physics_object.read(events)
        tau_m = self.physics_object.array[f"tau{self.m}"]
        tau_n = self.physics_object.array[f"tau{self.n}"]
        return tau_m / tau_n

    @property
    def config(self) -> dict:
        config = super().config
        config["m"] = self.m
        config["n"] = self.n

        return config

    @classmethod
    def from_config(cls, config: dict) -> Self:
        m = int(config["m"])
        n = int(config["n"])
        name = config.get("name")
        return cls(m=m, n=n, physics_object=config["physics_object"], name=name)
