import re
from abc import ABC, abstractmethod
from typing import Self

import awkward as ak
from typeguard import typechecked

from ..events import ROOTEvents
from ..types import AwkwardArray, Index


@typechecked
class PhysicsObject(ABC):
    def __init__(
        self,
        key: str,
        index: Index = slice(None),
        name: str | None = None,
    ) -> None:
        self._key = key
        self._index = index
        self._array = ak.Array([])
        self._name = name

    def __repr__(self) -> str:
        if not self.array.fields:
            return f"{self.name} -> not read yet"

        n_observables = len(self.array.fields)
        description = re.sub(
            r"\{.*?\}", f"{{{n_observables} observables}}", self.array.typestr
        )
        return f"{self.name} -> {description}"

    @property
    def key(self) -> str:
        return self._key

    @property
    def index(self) -> Index:
        return self._index

    @property
    def array(self) -> AwkwardArray:
        return self._array

    @abstractmethod
    def read(self, events: ROOTEvents) -> Self: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def config(self) -> dict: ...

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict) -> Self: ...
