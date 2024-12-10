from ..types import Self, typechecked
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

    def to_str(self) -> str:
        if self.start is None and self.stop is None:
            return ""

        elif self.start is None and self.stop is not None:
            return f":{self.stop}"

        elif self.start is not None and self.stop is None:
            return f"{self.start}:"

        else:
            return f"{self.start}:{self.stop}"

    @classmethod
    def from_str(cls, string: str) -> Self:
        if string == "":
            return cls()

        if ":" not in string:
            raise ValueError(f"Invalid string: {string}")

        parts = string.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid string: {string}")
        if any(not part.isdigit() for part in parts):
            raise ValueError(f"Invalid string: {string}")

        return cls(start=int(parts[0]), stop=int(parts[1]))

    @property
    def config(self) -> dict:
        return {"start": self.start, "stop": self.stop}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(start=config["start"], stop=config["stop"])
