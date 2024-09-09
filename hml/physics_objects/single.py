from abc import abstractmethod
from typing import Self

import awkward as ak
from typeguard import typechecked

from ..events import ROOTEvents
from ..naming import INDEX_PATTERN
from ..operations.awkward_ops import pad_none
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
@registered_object(f"(?P<key>(?:fat_?)?jet){INDEX_PATTERN}")
class Jet(Single):
    def __init__(
        self,
        key: str = "jet",
        index: int | slice = slice(None),
        name: str | None = None,
    ) -> None:
        super().__init__(key, index, name)

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        n_subjettiness = events[self.key + ".tau[5]"]

        array = ak.zip(
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

        return array


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
