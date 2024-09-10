from abc import abstractmethod
from typing import Literal, Self

import awkward as ak
import fastjet as fj
from typeguard import typechecked

from ..events import ROOTEvents
from ..naming import INDEX_PATTERN
from ..operations.awkward_ops import pad_none
from ..operations.fastjet_ops import get_algorithm
from ..operations.uproot_ops import constituents_to_momentum4d
from ..saving import registered_object
from ..types import AwkwardArray, Index, index_to_str, str_to_index
from .physics_object import PhysicsObject


@typechecked
class Single(PhysicsObject):
    def __init__(
        self,
        key: str,
        index: Index = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    @abstractmethod
    def get_array(self, events: ROOTEvents) -> AwkwardArray: ...

    def read(self, events: ROOTEvents) -> Self:
        array = self.get_array(events)

        if isinstance(self.index, int):
            target = self.index + 1
        elif self.index.stop is not None:
            target = self.index.stop
        else:
            target = None

        if target is not None:
            padded = pad_none(array, target, 1)
        else:
            padded = array

        self._array = padded[:, self.index]

        try:
            self._array = ak.to_regular(self._array, axis=None)
        except Exception:
            pass

        return self

    @property
    def name(self) -> str:
        if self._name:
            return self._name

        return self.key + index_to_str(self.index)

    @property
    def config(self) -> dict:
        return {
            "key": self.key,
            "index": index_to_str(self.index),
            "name": self._name,
        }

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(
            key=config["key"],
            index=str_to_index(config["index"]),
            name=config.get(
                "name"
            ),  # When retrieved from a pattern, name is not present
        )


@typechecked
@registered_object(f"(?P<key>electron){INDEX_PATTERN}")
class Electron(Single):
    def __init__(
        self,
        key: str = "electron",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.pt"]),
                "charge": events[f"{self.key}.charge"],
            }
        )

        return array


@typechecked
@registered_object(
    f"(?P<algorithm>(?:kt|ca|ak))?(?P<radius>[0-9]+)?(?P<key>(?:fat_?)?jet){INDEX_PATTERN}"
)
class Jet(Single):
    def __init__(
        self,
        algorithm: Literal["kt", "ca", "ak"] | None = None,
        radius: float | None = None,
        key: str = "jet",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)
        self.algorithm = algorithm
        self.radius = radius

    @property
    def name(self) -> str:
        name = super().name

        if self.algorithm is not None and self.radius is not None:
            name = f"{self.algorithm}{self.radius*10:.0f}{name}"

        return name

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        if self.algorithm is None or self.radius is None:
            n_subjettiness = events[self.key + ".tau[5]"]

            return ak.zip(
                {
                    "pt": events[self.key + ".pt"],
                    "eta": events[self.key + ".eta"],
                    "phi": events[self.key + ".phi"],
                    "mass": events[self.key + ".mass"],
                    "b_tag": events[self.key + ".b_tag"],
                    "tau_tag": events[self.key + ".tau_tag"],
                    "charge": events[self.key + ".charge"],
                    "tau1": n_subjettiness[..., 0],
                    "tau2": n_subjettiness[..., 1],
                    "tau3": n_subjettiness[..., 2],
                    "tau4": n_subjettiness[..., 3],
                    "tau5": n_subjettiness[..., 4],
                }
            )

        if "constituents" in self.key:
            key = events.mappings[self.key]
        else:
            key = events.mappings[self.key + ".constituents"]

        constituents_branch = events.tree[key]
        constituents = constituents_to_momentum4d(constituents_branch)
        self.constituents = ak.zip(
            {
                "pt": constituents.pt,
                "eta": constituents.eta,
                "phi": constituents.phi,
                "mass": constituents.mass,
            }
        )

        jet_def = fj.JetDefinition(get_algorithm(self.algorithm), self.radius)
        cluster = fj.ClusterSequence(ak.flatten(constituents, -1), jet_def)
        jets = cluster.inclusive_jets()
        sort_indices = ak.argsort(jets.pt, ascending=False)
        jets = ak.zip(
            {"pt": jets.pt, "eta": jets.eta, "phi": jets.phi, "mass": jets.mass}
        )
        jets = jets[sort_indices]

        return ak.values_astype(jets, "float32")

    @property
    def config(self) -> dict:
        config = super().config
        config["algorithm"] = self.algorithm
        config["radius"] = self.radius
        return config

    @classmethod
    def from_config(cls, config: dict) -> Self:
        radius = config.get("radius")
        if radius is not None:
            radius = radius if isinstance(radius, float) else float(radius) / 10

        return cls(
            algorithm=config.get("algorithm"),
            radius=radius,
            key=config["key"],
            index=str_to_index(config["index"]),
            name=config.get("name"),
        )


@typechecked
@registered_object(f"(?P<key>missing_et){INDEX_PATTERN}")
@registered_object(f"(?P<key>met){INDEX_PATTERN}")
class MissingET(Single):
    def __init__(
        self,
        key: str = "missing_et",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.met"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.met"]),
            }
        )

        return array


@typechecked
@registered_object(f"(?P<key>muon){INDEX_PATTERN}")
class Muon(Single):
    def __init__(
        self,
        key: str = "muon",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.pt"]),
                "charge": events[f"{self.key}.charge"],
            }
        )

        return array


@typechecked
@registered_object(f"(?P<key>photon){INDEX_PATTERN}")
class Photon(Single):
    def __init__(
        self,
        key: str = "photon",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.pt"]),
            }
        )

        return array


@typechecked
@registered_object(f"(?P<key>tower){INDEX_PATTERN}")
class Tower(Single):
    def __init__(
        self,
        key: str = "tower",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.et"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": ak.zeros_like(events[f"{self.key}.et"]),
            }
        )

        return array


@typechecked
@registered_object(f"(?P<key>track){INDEX_PATTERN}")
class Track(Single):
    def __init__(
        self,
        key: str = "track",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        array = ak.zip(
            {
                "pt": events[f"{self.key}.pt"],
                "eta": events[f"{self.key}.eta"],
                "phi": events[f"{self.key}.phi"],
                "mass": events[f"{self.key}.mass"],
            }
        )

        return array
