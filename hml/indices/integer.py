from ..types import Self, typechecked
from .base import Index


@typechecked
class IntegerIndex(Index):
    def __init__(self, value: int = 0) -> None:
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def to_str(self) -> str:
        return str(self.value)

    @classmethod
    def from_str(cls, string: str) -> Self:
        if not string.isdigit():
            raise ValueError(f"Invalid string: {string}")

        return cls(value=int(string))

    @property
    def config(self) -> dict:
        return {"value": self._value}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(value=config["value"])
