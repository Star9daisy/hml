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
from ..types import AwkwardArray, array_to_momentum, index_to_str, str_to_index
from .physics_object import PhysicsObject
from .single import Jet


@typechecked
class Nested(PhysicsObject):
    def __init__(self, source: PhysicsObject, **kwargs) -> None:
        super().__init__(**kwargs)
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

        if isinstance(self.source, Nested):
            indices = [self.source.source.index, self.source.index, self.index]
        else:
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
        source = retrieve(config["source"])

        if source is None:
            raise ValueError(f"Source {config['source']} not found")

        return cls(
            source=source,
            key=config["key"],
            index=str_to_index(config["index"]),
            name=config.get("name"),
        )


@typechecked
@registered_object(rf"(?P<source>[\w:._]+)\.(?P<key>constituents){INDEX_PATTERN}")
class Constituents(Nested):
    def __init__(self, source: PhysicsObject, **kwargs) -> None:
        super().__init__(source, **kwargs)

        if not isinstance(self.source, (Jet, Reclustered)):
            raise ValueError("Source currently must be a jet or a reclustered jet")

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        if isinstance(self.source, Reclustered):
            self.source.read(events)
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
    def __init__(self, source: PhysicsObject, **kwargs) -> None:
        super().__init__(source, **kwargs)

        if not isinstance(self.source, Jet):
            raise ValueError("Source must be a jet")

        if self.source.algorithm is None or self.source.radius is None:
            raise ValueError("Source must have algorithm and radius")

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        self.source.read(events)
        constituents = array_to_momentum(self.source.constituents)
        algorithm = self.source.algorithm
        radius = self.source.radius

        jet_def = fj.JetDefinition(get_algorithm(algorithm), radius)
        cluster = fj.ClusterSequence(constituents, jet_def)
        jets = cluster.inclusive_jets()

        sort_indices = ak.argsort(jets.pt, ascending=False)
        jets = ak.zip(
            {"pt": jets.pt, "eta": jets.eta, "phi": jets.phi, "mass": jets.mass}
        )
        jets = jets[sort_indices]
        self.constituents = ak.zip(
            {
                "pt": cluster.constituents().pt,
                "eta": cluster.constituents().eta,
                "phi": cluster.constituents().phi,
                "mass": cluster.constituents().mass,
            }
        )

        return ak.values_astype(jets, "float32")
