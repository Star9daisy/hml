import re
from abc import ABC, abstractmethod
from typing import Self

import awkward as ak
from inflection import underscore
from typeguard import typechecked

from ..events import ROOTEvents
from ..types import AwkwardArray, Index, index_to_str


@typechecked
class PhysicsObject(ABC):
    def __init__(
        self,
        key: str | None = None,
        index: Index | None = None,
        name: str | None = None,
    ) -> None:
        self._key = key if key is not None else underscore(self.__class__.__name__)
        self._index = index if index is not None else slice(None)
        self._array = ak.Array([])

        index_str = index_to_str(self._index)
        self._name = name if name is not None else f"{self.key}{index_str}"

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
    def name(self) -> str:
        return self._name

    @property
    @abstractmethod
    def config(self) -> dict: ...

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict) -> Self: ...
