from __future__ import annotations

from abc import ABC
from abc import abstractclassmethod
from abc import abstractmethod
from abc import abstractproperty
from typing import Any


class PhysicsObject(ABC):
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', value={self.value!r})"

    def __eq__(self, other: dict[str, Any]) -> bool:
        return self.config == other.config

    @abstractmethod
    def read_ttree(self, event: Any) -> PhysicsObject:
        ...

    @abstractproperty
    def name(self) -> str:
        ...

    @abstractproperty
    def value(self) -> Any:
        ...

    @abstractproperty
    def config(self) -> dict[str, Any]:
        ...

    @abstractclassmethod
    def from_name(cls, name: str) -> PhysicsObject:
        ...

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> PhysicsObject:
        return cls(**config)
