from __future__ import annotations

import re
from typing import Any

from .physics_object import PhysicsObject


def is_single_physics_object(identifier: str | PhysicsObject | None) -> bool:
    if identifier is None or identifier == "":
        return False

    if isinstance(identifier, PhysicsObject):
        identifier = identifier.name

    return bool(re.match(SinglePhysicsObject.pattern, identifier))


class SinglePhysicsObject(PhysicsObject):
    pattern = r"^([A-Za-z]+)(\d+)$"

    def __init__(self, type: str, index: int):
        self.type = type
        self.index = index

    def read(self, event):
        if self.type not in [i.GetName() for i in event.GetListOfBranches()]:
            raise ValueError(f"Branch {self.type} not found in event")

        branch = getattr(event, self.type)

        if self.index >= branch.GetEntries():
            return None

        return branch[self.index]

    @property
    def name(self) -> str:
        return f"{self.type}{self.index}"

    @classmethod
    def from_name(cls, name: str) -> SinglePhysicsObject:
        name = name.replace(" ", "")

        if (match := re.match(cls.pattern, name)) is None:
            raise ValueError(f"Could not parse name {name} as a single physics object")

        match = re.match(cls.pattern, name)
        type = match.group(1)
        index = int(match.group(2))
        return cls(type, index)

    @property
    def config(self) -> dict[str, Any]:
        config = {
            "class_name": "SinglePhysicsObject",
            "type": self.type,
            "index": self.index,
        }
        return config

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> SinglePhysicsObject:
        if config.get("class_name") != "SinglePhysicsObject":
            raise ValueError(f"Cannot parse config as SinglePhysicsObject: {config}")

        return cls(config["type"], config["index"])
