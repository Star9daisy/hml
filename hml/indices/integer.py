import re

from typeguard import typechecked

from ..types import Self
from .base import Index


@typechecked
class IntegerIndex(Index):
    PATTERN: re.Pattern[str] = re.compile(r"(?P<value>\d+)")

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
        if not (match := cls.PATTERN.fullmatch(name)):
            raise ValueError(f"Invalid name: {name}")

        value = int(match.groupdict()["value"])

        return cls(value=value)

    @property
    def config(self) -> dict:
        return {"value": self._value}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(value=config["value"])
