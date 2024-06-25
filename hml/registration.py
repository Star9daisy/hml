from __future__ import annotations

import re

from tinydb import Query, TinyDB
from typeguard import typechecked

from .config import REGISTRY_PATH
from .serialization import deserialize, serialize


def get_registry() -> TinyDB:
    """Get the registry."""
    return TinyDB(REGISTRY_PATH, indent=4)


def init_registry() -> None:
    """Initialize the registry."""
    db = get_registry()
    db.truncate()


@typechecked
def register(obj: object, name: str, existing_ok: bool = False):
    """Register an object as a string (its name)."""
    registered_name = name
    serialized_obj = serialize(obj)
    registered_info = {
        "registered_name": registered_name,
        "serialized_obj": serialized_obj,
    }

    registry = get_registry()
    if is_registered(registered_name):
        if existing_ok:
            registry.update(
                registered_info, Query()["registered_name"] == registered_name
            )
        else:
            raise ValueError(
                f"Object with name '{registered_name}' is already registered. No need to register it again."
            )

    else:
        registry.insert(registered_info)


@typechecked
def retrieve(name: str) -> object:
    """Retrieve an object from its name."""
    registry = get_registry()

    registered_item = None
    for item in registry:
        if re.fullmatch(item["registered_name"], name):
            registered_item = item

    if registered_item is None:
        raise ValueError(f"name '{name}' is not registered.")

    serialized_obj = registered_item["serialized_obj"]
    obj = deserialize(serialized_obj)

    return obj


@typechecked
def is_registered(name: str) -> bool:
    """Check if the name is registered."""
    registry = get_registry()

    return registry.contains(Query()["registered_name"] == name)


@typechecked
def is_covered(name: str) -> bool:
    """Check if the name is covered by a registered name."""
    registry = get_registry()
    registered_names = [item["registered_name"] for item in registry]

    for registered_name in registered_names:
        new_overlapped = re.fullmatch(registered_name, name)
        registered_overlapped = re.fullmatch(name, registered_name)

        if new_overlapped is not None or registered_overlapped is not None:
            return True

    return False


@typechecked
def show_registered_names(obj: object) -> list[str]:
    """Show registered names of an object."""
    registry = get_registry()

    serialized_obj = serialize(obj)
    items = registry.search(Query()["serialized_obj"].fragment(serialized_obj))
    names = [item["registered_name"] for item in items]
    return names


@typechecked
def search_registered_classes(name: str):
    """Search for registered classes."""
    registry = get_registry()

    for item in registry:
        if "config" not in item["serialized_obj"]:
            if item["registered_name"] in name:
                return item
