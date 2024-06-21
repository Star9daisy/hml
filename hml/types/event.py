from abc import ABC, abstractmethod
from typing import Self

import awkward as ak

from .aliases import PathLike


class Event(ABC):
    """Base abstract class for dict-like events.

    Events store the data as an awkward record array.
    """

    @property
    @abstractmethod
    def keys(self) -> list[str]:
        """Available keys of the events."""

    @abstractmethod
    def get(self, key: str) -> ak.Array | None:
        """Get the value according to the key."""

    @classmethod
    @abstractmethod
    def load(cls, path: PathLike) -> Self:
        """Load an event file from the given path."""
