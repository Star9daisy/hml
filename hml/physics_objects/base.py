from __future__ import annotations

import awkward as ak
from typeguard import typechecked

from ..types import Self, UprootTree


@typechecked
class PhysicsObject:
    def __init__(self, branch: str | PhysicsObject, class_name: str) -> None:
        self.branch = branch
        self.class_name = class_name

        self.array = ak.Array([])

    def __eq__(self, other: PhysicsObject) -> bool:
        if isinstance(other.branch, str):
            is_branch_same = self.branch == other.branch
        else:
            is_branch_same = self.branch.__eq__(other.branch)

        is_class_name_same = self.class_name == other.class_name

        return is_branch_same and is_class_name_same

    def __repr__(self) -> str:
        return f"{self.name!r}: {self.array.type!s}"

    def read(self, events: UprootTree) -> Self:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @classmethod
    def from_name(cls, name: str) -> PhysicsObject:
        raise NotImplementedError

    @property
    def config(self) -> dict:
        branch = self.branch
        class_name = self.class_name

        return {"branch": branch, "class_name": class_name}

    @classmethod
    def from_config(cls, config: dict) -> PhysicsObject:
        branch = config["branch"]
        class_name = config["class_name"]

        return cls(branch=branch, class_name=class_name)


@typechecked
class SinglePhysicsObject(PhysicsObject):
    def __init__(self, branch: str, class_name: str) -> None:
        super().__init__(branch=branch, class_name=class_name)

    @property
    def name(self) -> str:
        return self.class_name

    @classmethod
    def from_name(cls, name: str) -> SinglePhysicsObject:
        return cls(branch=cls.__name__, class_name=name)


@typechecked
class NestedPhysicsObject(PhysicsObject):
    def __init__(
        self,
        branch: SinglePhysicsObject | NestedPhysicsObject,
        class_name: str,
    ) -> None:
        super().__init__(branch=branch, class_name=class_name)

    @property
    def name(self) -> str:
        return f"{self.branch.name}.{self.class_name}"

    @classmethod
    def from_name(cls, name: str) -> NestedPhysicsObject:
        raise NotImplementedError
