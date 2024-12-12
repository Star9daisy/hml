from importlib import import_module

from typeguard import typechecked

from .base import Index
from .integer import IntegerIndex
from .range import RangeIndex


@typechecked
def serialize(index: Index) -> dict:
    return {
        "module": index.__module__,
        "class_name": index.__class__.__name__,
        "config": index.config,
    }


@typechecked
def deserialize(dict_: dict) -> Index:
    module = import_module(dict_["module"])
    class_ = getattr(module, dict_["class_name"])

    return class_.from_config(dict_["config"])


@typechecked
def get(name: str) -> Index:
    if name.isdigit():
        return IntegerIndex.from_name(name)

    elif name == "" or ":" in name:
        return RangeIndex.from_name(name)

    else:
        raise ValueError(f"Invalid name: {name}")
