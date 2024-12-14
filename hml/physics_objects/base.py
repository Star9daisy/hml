from ..indices import Index
from ..types import AwkwardArray, ROOTEvents, Self


class PhysicsObject:
    PATTERN: str

    def __repr__(self) -> str:
        return f"{self.name}: {self.array.typestr}"

    @property
    def branch(self) -> str:
        raise NotImplementedError

    @property
    def index(self) -> Index:
        raise NotImplementedError

    @property
    def array(self) -> AwkwardArray:
        raise NotImplementedError

    def get_array(self, events: ROOTEvents) -> AwkwardArray:
        raise NotImplementedError

    def read(self, events: ROOTEvents) -> Self:
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
