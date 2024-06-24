from abc import ABC, abstractmethod
from typing import Self

import awkward as ak
import uproot

from .aliases import IndexLike
from .event import Event


class PhysicsObject(ABC):
    """Base abstract class for physics objects."""

    @property
    @abstractmethod
    def key(self) -> str:
        """The key name of the physics object."""

    @property
    @abstractmethod
    def indices(self) -> list[IndexLike]:
        """The indices of the physics object."""

    @property
    @abstractmethod
    def p4(self) -> ak.Array:
        """The momentum 4D of the physics object."""

    @abstractmethod
    def read(self, events: uproot.TTree | Event) -> Self:
        """Read events to fetch the p4."""
