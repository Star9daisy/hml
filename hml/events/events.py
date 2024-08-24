from abc import ABC, abstractmethod

from ..types import AwkwardArray


class Events(ABC):
    """Abstract base class for events classes.

    The following methods with the given signatures must be implemented by the
    child classes:
    - __getitem__(self, key: str) -> AwkwardArray
    - __len__(self) -> int
    """

    @abstractmethod
    def __getitem__(self, key: str) -> AwkwardArray: ...

    @abstractmethod
    def __len__(self) -> int: ...
