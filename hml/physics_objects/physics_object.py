import re
from typing import Self

import awkward as ak
import uproot

from ..events import DelphesEvent
from ..naming import index_to_str, str_to_index
from ..operations import awkward_ops as ako
from ..operations import uproot_ops as upo
from ..types import IndexLike, PhysicsObject


class PhysicsObjectBase(PhysicsObject):
    """Base class for physics objects.

    Following the naming convention, the name of the physics object is composed
    of the key and the indices. The key is used to access the data in the
    events, and the indices are used to select the data.

    Parameters
    ----------
    key : str, optional
        The key name of the physics object.
    indices : IndexLike | list[IndexLike], optional
        The indices of the physics object.
    """

    def __init__(
        self,
        key: str | None = None,
        indices: IndexLike | list[IndexLike] | None = None,
    ) -> None:
        self._key = key
        self._indices = indices
        self._values = None

    @property
    def key(self) -> str:
        """The key name of the physics object."""
        if self._key is None:
            return self.__class__.__name__

        return self._key

    @property
    def indices(self) -> list[IndexLike]:
        """The indices of the physics object."""
        if self._indices is None:
            indices = [slice(None)] * len(self.key.split("."))
        else:
            indices = (
                [self._indices] if isinstance(self._indices, int) else self._indices
            )

        indices = [slice(None)] + indices
        return indices

    @property
    def p4(self) -> ak.Array:
        """The momentum 4D of the physics object."""
        slices = [slice(i, i + 1) if isinstance(i, int) else i for i in self.indices]
        values = ako.take(self._values, slices)

        axes_to_squeeze = []
        for i, index in enumerate(self.indices):
            if isinstance(index, slice):
                if index.stop is not None:
                    start = index.start or 0
                    required_length = index.stop - start
                    values = ako.pad_none(values, required_length, axis=i)

            else:
                axes_to_squeeze.append(i)

        values = ako.squeeze(values, axis=axes_to_squeeze)

        return values

    def read(self, events: uproot.TTree | DelphesEvent) -> Self:
        """Read events to fetch the p4."""
        if isinstance(events, uproot.TTree):
            self.events = DelphesEvent(events)
        else:
            self.events = events

        key = self.events.keys_dict[self.key]
        self._values = upo.branch_to_momentum4d(self.events.tree[key])
        return self

    @property
    def name(self) -> str:
        keys = self.key.split(".")
        indices = self.indices[1:]
        name = ".".join(key + index_to_str(index) for key, index in zip(keys, indices))

        return name

    @classmethod
    def from_name(cls, name: str) -> Self:
        key_pattern = rf"({cls.__name__}|{cls.__name__.lower()})"
        indices_pattern = r"(\d*:?\d*)"
        match = re.fullmatch(rf"{key_pattern}{indices_pattern}", name)
        key, indices = match.groups()
        indices = [str_to_index(indices)]

        return cls(key=key, indices=indices)

    @property
    def config(self) -> dict:
        return {
            "key": self.key,
            "indices": [index_to_str(index) for index in self.indices[1:]],
        }

    @classmethod
    def from_config(cls, config: dict):
        indices = config["indices"]
        config["indices"] = [str_to_index(index) for index in indices]

        return cls(**config)
