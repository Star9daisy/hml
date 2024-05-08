from __future__ import annotations

from abc import ABC, abstractmethod


class PhysicsObject(ABC):
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        configs = []
        for key, value in self.config.items():
            if isinstance(value, str):
                configs.append(f"{key}='{value}'")
            else:
                configs.append(f"{key}={value}")
        configs = ", ".join(configs)

        return f"{self.__class__.__name__}({configs})"

    @property
    @abstractmethod
    def branch(self) -> str: ...

    @property
    @abstractmethod
    def slices(self) -> list[slice]: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def config(self) -> dict: ...

    @classmethod
    @abstractmethod
    def from_name(cls, name: str) -> PhysicsObject: ...

    @classmethod
    def from_config(cls, config: dict) -> PhysicsObject: ...
