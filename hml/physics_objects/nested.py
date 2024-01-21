from __future__ import annotations

import re
from importlib import import_module
from typing import Any

from .collective import CollectivePhysicsObject
from .physics_object import PhysicsObject
from .single import SinglePhysicsObject
from .single import is_single_physics_object


def is_nested_physics_object(identifier: str | PhysicsObject | None) -> bool:
    if identifier is None or identifier == "":
        return False

    if isinstance(identifier, PhysicsObject):
        identifier = identifier.name

    return bool(re.match(NestedPhysicsObject.pattern, identifier))


class NestedPhysicsObject(PhysicsObject):
    pattern = r"^([A-Za-z]+\d*:?\d*)\.([A-Za-z]+\d*:?\d*)$"

    def __init__(
        self,
        main: SinglePhysicsObject | CollectivePhysicsObject,
        sub: SinglePhysicsObject | CollectivePhysicsObject,
    ):
        self.main = main
        self.sub = sub

        self._name = None

    def read(self, event):
        ALL_LEAVES = [i.GetName() for i in event.GetListOfLeaves()]
        if f"{self.main.type}.{self.sub.type}" not in ALL_LEAVES:
            raise ValueError(
                f"Leave {self.main.type}.{self.sub.type} not found in event"
            )

        main_objects = self.main.read(event)
        main_objects = (
            main_objects if isinstance(main_objects, list) else [main_objects]
        )

        sub_objects = []
        for main_object in main_objects:
            if main_object is None:
                if isinstance(self.sub, SinglePhysicsObject):
                    sub_objects.append(None)
                else:
                    sub_objects.append([None])
            else:
                leaves = list(getattr(main_object, self.sub.type))
                if isinstance(self.sub, SinglePhysicsObject):
                    if self.sub.index >= len(leaves):
                        sub_objects.append(None)
                    else:
                        sub_objects.append(leaves[self.sub.index])
                else:
                    if self.sub.start is None and self.sub.end is None:
                        sub_objects.append(leaves)
                    elif self.sub.end is None:
                        sub_objects.append(leaves[self.sub.start :])
                    elif self.sub.start is None:
                        objects = leaves[: self.sub.end]
                        if len(objects) < self.sub.end:
                            objects += [None] * (self.sub.end - len(objects))
                        sub_objects.append(objects)
                    else:
                        objects = leaves[self.sub.start : self.sub.end]
                        if len(objects) < self.sub.end - self.sub.start:
                            objects += [None] * (
                                self.sub.end - self.sub.start - len(objects)
                            )
                        sub_objects.append(objects)

        return sub_objects

    @property
    def name(self) -> str:
        if self._name is not None:
            return self._name

        return f"{self.main.name}.{self.sub.name}"

    @classmethod
    def from_name(cls, name: str) -> NestedPhysicsObject:
        name = name.replace(" ", "")

        if (match := re.match(cls.pattern, name)) is None:
            raise ValueError(f"Could not parse name {name} as a nested physics object")

        # main --------------------------------------------------------------- #
        main_match = match.group(1)
        if is_single_physics_object(main_match):
            main = SinglePhysicsObject.from_name(main_match)
        else:
            main = CollectivePhysicsObject.from_name(main_match)

        # sub ---------------------------------------------------------------- #
        sub_match = match.group(2)
        if is_single_physics_object(sub_match):
            sub = SinglePhysicsObject.from_name(sub_match)
        else:
            sub = CollectivePhysicsObject.from_name(sub_match)

        instance = cls(main, sub)
        instance._name = name
        return instance

    @property
    def config(self) -> dict[str, Any]:
        config = {
            "class_name": "NestedPhysicsObject",
            "main_config": self.main.config,
            "sub_config": self.sub.config,
        }
        return config

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> NestedPhysicsObject:
        if config.get("class_name") != "NestedPhysicsObject":
            raise ValueError(f"Cannot parse config as NestedPhysicsObject: {config}")

        module = import_module("hml.physics_objects")

        # main --------------------------------------------------------------- #
        main_class_name = config["main_config"]["class_name"]
        main_class = getattr(module, main_class_name)
        main = main_class.from_config(config["main_config"])

        # sub ---------------------------------------------------------------- #
        sub_class_name = config["sub_config"]["class_name"]
        sub_class = getattr(module, sub_class_name)
        sub = sub_class.from_config(config["sub_config"])

        return cls(main, sub)
