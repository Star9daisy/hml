from typeguard import typechecked

from ..types import Self


@typechecked
class Index:
    PATTERN: str = r"\d*:?\d*"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    @property
    def value(self) -> int | slice:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_name(cls, name: str) -> Self:
        raise NotImplementedError

    @property
    def config(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: dict) -> Self:
        raise NotImplementedError
