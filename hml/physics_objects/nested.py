from abc import abstractmethod
from typing import Self

import awkward as ak
import fastjet as fj
from typeguard import typechecked

from ..events import ROOTEvents
from ..naming import INDEX_PATTERN
from ..operations.awkward_ops import pad_none
from ..operations.fastjet_ops import get_algorithm
from ..saving import registered_object, retrieve
from ..types import AwkwardArray, index_to_str, str_to_index
from .physics_object import PhysicsObject


@typechecked
class Nested(PhysicsObject):
    def __init__(self, source: str | PhysicsObject, **kwargs) -> None:
        super().__init__(**kwargs)

        if isinstance(source, str):
            self._source = retrieve(source)
            if self._source is None:
                raise ValueError(f"Physics object {self._source} not found")
        else:
            self._source = source

        if kwargs.get("name") is None:
            self._name = self.source.name + "." + self._name

    @property
    def source(self) -> PhysicsObject:
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
@registered_object(rf"(?P<source>[\w:._]+)\.(?P<key>constituents){INDEX_PATTERN}")
class Constituents(Nested):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        self.source.read(events)
        if hasattr(self.source, "constituents"):
            return self.source.constituents

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


@typechecked
@registered_object(rf"(?P<source>[\w:._]+)\.(?P<key>reclustered){INDEX_PATTERN}")
class Reclustered(Nested):
    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        self.source.read(events)

        self.constituents = self.source.constituents
        self.algorithm = self.source.algorithm
        self.radius = self.source.radius

        jet_def = fj.JetDefinition(get_algorithm(self.algorithm), self.radius)
        cluster = fj.ClusterSequence(self.constituents, jet_def)
        jets = cluster.inclusive_jets()
        sort_indices = ak.argsort(jets.pt, ascending=False)
        jets = ak.zip(
            {"pt": jets.pt, "eta": jets.eta, "phi": jets.phi, "mass": jets.mass}
        )
        jets = jets[sort_indices]

        return ak.values_astype(jets, "float32")
