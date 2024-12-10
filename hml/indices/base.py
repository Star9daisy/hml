from ..types import Self, typechecked


@typechecked
class Index:
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={self.value})"

    @property
    def value(self) -> int | slice:
        raise NotImplementedError

    def to_str(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_str(cls, string: str) -> Self:
        raise NotImplementedError

    @property
    def config(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_config(cls, config: dict) -> Self:
        raise NotImplementedError
