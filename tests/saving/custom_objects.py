from typing import Self

from hml.saving import registered_object


@registered_object("toy")
class Toy:
    def __init__(self, arg1: int, arg2: int) -> None:
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def config(self) -> dict:
        return {"arg1": self.arg1, "arg2": self.arg2}

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls(**config)

    @property
    def name(self) -> str:
        return f"toy{self.arg1}{self.arg2}"

    @classmethod
    def from_name(cls, name: str) -> Self:
        arg1 = int(name[-2])
        arg2 = int(name[-1])

        return cls(arg1, arg2)
