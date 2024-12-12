from typeguard import typechecked

from ..types import Self
from .base import Index


@typechecked
class RangeIndex(Index):
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
        if name == "":
            return cls()

        if ":" not in name:
            raise ValueError(f"Invalid name: {name}")

        parts = name.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid name: {name}")

        if any(not part.isdigit() for part in parts):
            raise ValueError(f"Invalid name: {name}")

        return cls(start=int(parts[0]), stop=int(parts[1]))

    @property
    def config(self) -> dict:
        return {"start": self.start, "stop": self.stop}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(start=config["start"], stop=config["stop"])
