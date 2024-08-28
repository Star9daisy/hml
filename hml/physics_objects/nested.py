from abc import abstractmethod
from typing import Self

import awkward as ak
from typeguard import typechecked

from ..events import ROOTEvents
from ..naming import INDEX_PATTERN
from ..operations.awkward_ops import pad_none
from ..saving import registered_object, retrieve
from ..types import AwkwardArray, Index, index_to_str, str_to_index
from .physics_object import PhysicsObject
from .single import Single


@typechecked
class Nested(PhysicsObject):
    def __init__(
        self,
        source: str | Single,
        key: str,
        index: Index = slice(None),
        name: str | None = None,
    ) -> None:

        if isinstance(source, str):
            self._source = retrieve(source)
            if self._source is None:
                raise ValueError(f"Physics object {self._source} not found")
        else:
            self._source = source

        super().__init__(key, index, name)

    @property
    def source(self) -> Single:
        return self._source

    @abstractmethod
    def get_array(self, events) -> AwkwardArray: ...

    def read(self, events):
        array = self.get_array(events)
        indices = [self.source.index, self.index]
        for i, index in enumerate(indices, start=1):
            if isinstance(index, int):
                target = index + 1
            elif index.stop is not None:
                target = index.stop
            else:
                target = None

            if target is not None:
                array = pad_none(array, target, i)

        self._array = array[tuple([slice(None), *indices])]

        try:
            self._array = ak.to_regular(self._array, axis=None)
        except Exception:
            pass

        return self

    @property
    def name(self) -> str:
        if self._name:
            return self._name

        return f"{self.source.name}.{self.key}{index_to_str(self.index)}"

    @property
    def config(self) -> dict:
        return {
            "source": self.source.name,
            "key": self.key,
            "index": index_to_str(self.index),
            "name": self._name,
        }

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(
            source=config["source"],
            key=config["key"],
            index=str_to_index(config["index"]),
            name=config.get("name"),
        )


@typechecked
@registered_object(
    f"(?P<source>[a-zA-Z_]+\d*:?\d*)\.(?P<key>constituents){INDEX_PATTERN}"
)
class Constituents(Nested):
    def __init__(
        self,
        source: str | Single,
        key: str = "constituents",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(source, key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = events[self.source.key + "." + self.key]
        array = ak.zip(
            {
                "pt": array.pt,
                "eta": array.eta,
                "phi": array.phi,
                "mass": array.mass,
            }
        )

        return array
