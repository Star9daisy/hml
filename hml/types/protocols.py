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
    """Registrable objects have a name and can be created from it.

    This protocol extends `Serializable` with:
    - `name` property
    - `from_name` class method
    """

    @property
    def name(self) -> str: ...

    @classmethod
    def from_name(cls, name: str) -> Self: ...
