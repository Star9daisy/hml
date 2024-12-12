from typeguard import typechecked

from ..types import Self
from .base import Index


@typechecked
class IntegerIndex(Index):
    def __init__(self, value: int = 0) -> None:
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @property
    def name(self) -> str:
        return str(self.value)

    @classmethod
    def from_name(cls, name: str) -> Self:
        if not name.isdigit():
            raise ValueError(f"Invalid name: {name}")

        return cls(value=int(name))

    @property
    def config(self) -> dict:
        return {"value": self._value}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(value=config["value"])
