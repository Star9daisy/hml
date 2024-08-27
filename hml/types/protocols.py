from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    """Serializable objects can be converted to and from a dictionary.

    This protocol requires two parts:
    - `config` property returns a dictionary representation of the object
    - `from_config` class method creates an object from a dictionary
    """

    @property
    def config(self) -> dict: ...

    @classmethod
    def from_config(cls, config: dict) -> Self: ...


@runtime_checkable
class Registrable(Serializable, Protocol):
    """Registrable objects have an intrinsic name for registration.

    This protocol extends `Serializable` with:
    - `name` property
    """

    @property
    def name(self) -> str: ...
