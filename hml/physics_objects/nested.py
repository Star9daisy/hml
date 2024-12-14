import re
from importlib import import_module

import awkward as ak
from inflection import underscore
from typeguard import typechecked

from ..indices import Index, IndexLike, IntegerIndex, RangeIndex, index_like_to_index
from ..indices import deserialize as deserialize_index
from ..indices import retrieve as retrieve_index
from ..indices import serialize as serialize_index
from ..operations import awkward as oak
from ..operations import fastjet as ofj
from ..operations import uproot as our
from ..types import (
    AwkwardArray,
    ROOTEvents,
    Self,
    momentum_to_array,
    pxpypze_to_ptetaphim,
)
from .base import PhysicsObject
from .single import FatJet, Jet, SinglePhysicsObject


@typechecked
class NestedPhysicsObject(PhysicsObject):
    PATTERN: str = rf"{SinglePhysicsObject.PATTERN}(?:\.{SinglePhysicsObject.PATTERN})+"

    def __init__(
        self,
        parent: "SinglePhysicsObject | NestedPhysicsObject",
        index: IndexLike | None = None,
    ) -> None:
        self.parent = parent
        self._branch = self.__class__.__name__
        self.branch_name = underscore(self._branch)
        self._index = index
        self._array = oak.empty_array()

    @property
    def branch(self) -> str:
        return self._branch

    @property
    def index(self) -> Index:
        if self._index is None:
            return RangeIndex()
        else:
            return index_like_to_index(self._index)

    @property
    def array(self) -> AwkwardArray:
        return self._array

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        raise NotImplementedError

    def read(self, events: ROOTEvents) -> Self:
        array = self.get_array(events)

        if isinstance(self.parent, SinglePhysicsObject):
            indices = [self.parent.index, self.index]
        else:
            parent = self.parent
            indices = []
            while isinstance(parent, NestedPhysicsObject):
                indices.append(parent.index)
                parent = parent.parent

        for i, index in enumerate(indices, start=1):
            if isinstance(index, IntegerIndex):
                array = oak.pad_none(array, index.value + 1, axis=i)
            elif isinstance(index, RangeIndex):
                if index.stop is not None:
                    array = oak.pad_none(array, index.stop, axis=i)
            else:
                raise TypeError(f"Invalid index: {index}")

        indexed = oak.take(array, indices)

        try:
            regular = ak.to_regular(indexed, axis=None)
        except Exception:
            regular = indexed

        self._array = regular

        return self

    @property
    def shape(self) -> tuple[int, ...]:
        return oak.get_shape(self.array)

    @property
    def dtype(self) -> dict[str, str]:
        return oak.get_record_dtype(self.array)

    @property
    def name(self) -> str:
        return f"{self.parent.name}.{self.branch_name + self.index.name}"

    @classmethod
    def from_name(cls, name: str) -> Self:
        raise NotImplementedError

    @property
    def config(self) -> dict:
        return {
            "parent": {
                "module": self.parent.__module__,
                "class_name": self.parent.__class__.__name__,
                "config": self.parent.config,
            },
            "index": serialize_index(self.index),
        }

    @classmethod
    def from_config(cls, config: dict) -> Self:
        parent_module = import_module(config["parent"]["module"])
        parent_cls = getattr(parent_module, config["parent"]["class_name"])
        parent = parent_cls.from_config(config["parent"]["config"])
        index = deserialize_index(config["index"])

        return cls(parent=parent, index=index)


@typechecked
class Reclustered(NestedPhysicsObject):
    PATTERN: str = rf"(?P<parent>\w+?\d+(?:fat)?jet{Index.PATTERN})\.reclustered(?P<index>{Index.PATTERN})"

    def __init__(self, parent: Jet, index: IndexLike | None = None) -> None:
        super().__init__(parent, index)

        # To ensure the type of parent is Jet for Pyright
        self.parent = parent

        if self.parent.algorithm is None or self.parent.radius is None:
            raise ValueError(f"Invalid parent: {parent}")

        self.algorithm = self.parent.algorithm
        self.radius = self.parent.radius

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        branch = f"{self.parent.branch}.Constituents"
        constituents = our.get_branch(events, branch, as_momentum=True)

        jets, constituents = ofj.get_inclusive_jets(
            constituents,
            radius=self.radius,
            algorithm=self.algorithm,
        )

        jets = momentum_to_array(pxpypze_to_ptetaphim(jets))
        constituents = momentum_to_array(pxpypze_to_ptetaphim(constituents))
        self.constituents = ak.values_astype(constituents, "float32")

        return ak.values_astype(jets, "float32")

    @classmethod
    def from_name(cls, name: str) -> Self:
        if not (match := re.fullmatch(cls.PATTERN, name)):
            raise ValueError(f"Invalid name: {name}")

        group = match.groupdict()
        branch = group.get("branch")

        if re.fullmatch(Jet.PATTERN, group["parent"]):
            parent = Jet.from_name(group["parent"])
        elif re.fullmatch(FatJet.PATTERN, group["parent"]):
            parent = FatJet.from_name(group["parent"])
        else:
            raise ValueError(f"Invalid parent: {group['parent']}")

        index = retrieve_index(group["index"])

        obj = cls(parent=parent, index=index)
        obj.branch_name = branch or underscore(cls.__name__)

        return obj


@typechecked
class Constituents(NestedPhysicsObject):
    PATTERN: str = rf"(?P<parent>\w+\d+(?:fat)?jet{Index.PATTERN}(?:\.reclustered{Index.PATTERN})?)\.constituents(?P<index>{Index.PATTERN})"

    def __init__(
        self, parent: Jet | Reclustered, index: IndexLike | None = None
    ) -> None:
        super().__init__(parent, index)

        # To ensure the type of parent is Jet for Pyright
        self.parent = parent

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return self.parent.read(events).constituents

    @classmethod
    def from_name(cls, name: str) -> Self:
        if not (match := re.fullmatch(cls.PATTERN, name)):
            raise ValueError(f"Invalid name: {name}")

        group = match.groupdict()
        branch = group.get("branch")

        if re.fullmatch(Jet.PATTERN, group["parent"]):
            parent = Jet.from_name(group["parent"])
        elif re.fullmatch(FatJet.PATTERN, group["parent"]):
            parent = FatJet.from_name(group["parent"])
        elif re.fullmatch(Reclustered.PATTERN, group["parent"]):
            parent = Reclustered.from_name(group["parent"])
        else:
            raise ValueError(f"Invalid parent: {group['parent']}")

        index = retrieve_index(group["index"])

        obj = cls(parent=parent, index=index)
        obj.branch_name = branch or underscore(cls.__name__)

        return obj
