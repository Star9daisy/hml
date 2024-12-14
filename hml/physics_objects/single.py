import re

import awkward as ak
from inflection import underscore
from particle import Particle
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


@typechecked
class SinglePhysicsObject(PhysicsObject):
    PATTERN: str = rf"[a-zA-Z]+\w*[a-zA-Z]+{Index.PATTERN}"

    def __init__(self, index: IndexLike | None = None) -> None:
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

        if isinstance(self.index, IntegerIndex):
            padded = oak.pad_none(array, self.index.value + 1, axis=1)
        elif isinstance(self.index, RangeIndex):
            if self.index.stop is not None:
                padded = oak.pad_none(array, self.index.stop, axis=1)
            else:
                padded = array
        else:
            raise ValueError(f"Invalid index: {self.index}")

        indexed = oak.take(padded, self.index)

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
        return self.branch_name + self.index.name

    @classmethod
    def from_name(cls, name: str) -> Self:
        if not (match := re.fullmatch(cls.PATTERN, name)):
            raise ValueError(f"Invalid name: {name}")

        group = match.groupdict()
        branch = group.get("branch")
        index = retrieve_index(group["index"])

        obj = cls(index=index)
        obj.branch_name = branch or underscore(cls.__name__)

        return obj

    @property
    def config(self) -> dict:
        return {"index": serialize_index(self.index)}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(index=(deserialize_index(config["index"])))


@typechecked
class Electron(SinglePhysicsObject):
    PATTERN: str = rf"electron(?P<index>{Index.PATTERN})"
    MASS: float = Particle.from_name("e-").mass  # type: ignore

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "m": ak.full_like(events[f"{self.branch}.PT"].array(), self.MASS),
                "q": events[f"{self.branch}.Charge"].array(),
            }
        )


@typechecked
class Jet(SinglePhysicsObject):
    PATTERN: str = rf"(?P<algorithm>\w+?)(?P<radius>\d+)jet(?P<index>{Index.PATTERN})"

    def __init__(
        self,
        algorithm: str | None = None,
        radius: float | None = None,
        index: IndexLike | None = None,
    ) -> None:
        super().__init__(index=index)
        self.algorithm = algorithm
        self.radius = radius

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        if self.algorithm is None or self.radius is None:
            constituents_branch = f"{self.branch}.Constituents"
            constituents = our.get_branch(events, constituents_branch)
            self.constituents = ak.values_astype(constituents, "float32")

            n_subjettiness = events[f"{self.branch}.Tau[5]"].array()

            return ak.zip(
                {
                    "pt": events[f"{self.branch}.PT"].array(),
                    "eta": events[f"{self.branch}.Eta"].array(),
                    "phi": events[f"{self.branch}.Phi"].array(),
                    "m": events[f"{self.branch}.Mass"].array(),
                    "b_tag": events[f"{self.branch}.BTag"].array(),
                    "tau_tag": events[f"{self.branch}.TauTag"].array(),
                    "q": events[f"{self.branch}.Charge"].array(),
                    "tau1": n_subjettiness[..., 0],
                    "tau2": n_subjettiness[..., 1],
                    "tau3": n_subjettiness[..., 2],
                    "tau4": n_subjettiness[..., 3],
                    "tau5": n_subjettiness[..., 4],
                }
            )
        else:
            constituents_branch = f"{self.branch}.Constituents"
            constituents = our.get_branch(events, constituents_branch, as_momentum=True)
            flattened_constituents = ak.flatten(constituents, axis=-1)

            jets, constituents = ofj.get_inclusive_jets(
                flattened_constituents,
                radius=self.radius,
                algorithm=self.algorithm,
            )
            jets = momentum_to_array(pxpypze_to_ptetaphim(jets))
            constituents = momentum_to_array(pxpypze_to_ptetaphim(constituents))
            self.constituents = ak.values_astype(constituents, "float32")

            return ak.values_astype(jets, "float32")

    @property
    def name(self) -> str:
        if self.algorithm is None or self.radius is None:
            return super().name
        else:
            return f"{self.algorithm}{self.radius*10:.0f}" + super().name

    @classmethod
    def from_name(cls, name: str) -> Self:
        if not (match := re.fullmatch(cls.PATTERN, name)):
            raise ValueError(f"Invalid name: {name}")

        group = match.groupdict()
        algorithm = group["algorithm"]
        radius = float(group["radius"]) / 10
        branch = group.get("branch")
        index = retrieve_index(group["index"])

        obj = cls(algorithm=algorithm, radius=radius, index=index)
        obj.branch_name = branch or underscore(cls.__name__)

        return obj

    @property
    def config(self) -> dict:
        config = super().config
        config["algorithm"] = self.algorithm
        config["radius"] = self.radius

        return config

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(
            algorithm=config["algorithm"],
            radius=config["radius"],
            index=deserialize_index(config["index"]),
        )


@typechecked
class FatJet(Jet):
    PATTERN: str = rf"(?P<algorithm>\w+?)(?P<radius>\d+)(?P<branch>fatjet)(?P<index>{Index.PATTERN})"


@typechecked
class MissingET(SinglePhysicsObject):
    PATTERN: str = rf"(?P<branch>missing_et|met)(?P<index>{Index.PATTERN})"

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return ak.zip(
            {
                "pt": events[f"{self.branch}.MET"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "m": ak.zeros_like(events[f"{self.branch}.MET"].array()),
            }
        )


@typechecked
class Muon(SinglePhysicsObject):
    PATTERN: str = rf"muon(?P<index>{Index.PATTERN})"
    MASS: float = Particle.from_name("mu-").mass  # type: ignore

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "m": ak.full_like(events[f"{self.branch}.PT"].array(), self.MASS),
                "q": events[f"{self.branch}.Charge"].array(),
            }
        )


@typechecked
class Photon(SinglePhysicsObject):
    PATTERN: str = rf"photon(?P<index>{Index.PATTERN})"

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "m": ak.zeros_like(events[f"{self.branch}.PT"].array()),
            }
        )


@typechecked
class Tower(SinglePhysicsObject):
    PATTERN: str = rf"tower(?P<index>{Index.PATTERN})"

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return ak.zip(
            {
                "pt": events[f"{self.branch}.ET"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "m": ak.zeros_like(events[f"{self.branch}.ET"].array()),
            }
        )


@typechecked
class Track(SinglePhysicsObject):
    PATTERN: str = rf"track(?P<index>{Index.PATTERN})"

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        return ak.zip(
            {
                "pt": events[f"{self.branch}.PT"].array(),
                "eta": events[f"{self.branch}.Eta"].array(),
                "phi": events[f"{self.branch}.Phi"].array(),
                "m": events[f"{self.branch}.Mass"].array(),
            }
        )
