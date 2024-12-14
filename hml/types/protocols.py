import re
from typing import runtime_checkable

from .builtins import Protocol, Self


@runtime_checkable
class Serializable(Protocol):
    @property
    def config(self) -> dict: ...

    @classmethod
    def from_config(cls, config: dict) -> Self: ...


@runtime_checkable
class Registrable(Protocol):
    PATTERN: re.Pattern[str]

    @property
    def config(self) -> dict: ...

    @classmethod
    def from_config(cls, config: dict) -> Self: ...

    @property
    def name(self) -> str: ...

    @classmethod
    def from_name(cls, name: str) -> Self: ...
