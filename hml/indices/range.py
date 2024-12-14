import re

from typeguard import typechecked

from ..types import Self
from .base import Index


@typechecked
class RangeIndex(Index):
    PATTERN: str = r"(?:(?P<start>\d+)?:(?P<stop>\d+)?)?"

    def __init__(self, start: int | None = None, stop: int | None = None) -> None:
        self.start = start
        self.stop = stop
        self._value = slice(start, stop)

    @property
    def value(self) -> slice:
        return self._value

    @property
    def name(self) -> str:
        if self.start is None and self.stop is None:
            return ""

        elif self.start is not None and self.stop is None:
            return f"{self.start}:"

        elif self.start is None and self.stop is not None:
            return f":{self.stop}"

        else:
            return f"{self.start}:{self.stop}"

    @classmethod
    def from_name(cls, name: str) -> Self:
        if not (match := re.fullmatch(cls.PATTERN, name)):
            raise ValueError(f"Invalid name: {name}")

        group = match.groupdict()
        start, stop = group["start"], group["stop"]
        start = int(start) if start is not None else start
        stop = int(stop) if stop is not None else stop

        return cls(start=start, stop=stop)

    @property
    def config(self) -> dict:
        return {"start": self.start, "stop": self.stop}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(start=config["start"], stop=config["stop"])
