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
    if "module" in dict_ and "class_name" in dict_:
        module = import_module(dict_["module"])
        class_ = getattr(module, dict_["class_name"])
        return class_.from_config(dict_["config"])

    else:
        if "value" in dict_:
            return IntegerIndex.from_config(dict_)
        elif "start" in dict_ and "stop" in dict_:
            return RangeIndex.from_config(dict_)
        else:
            raise ValueError(f"Invalid dict: {dict_}")


@typechecked
def get(name: str) -> Index:
    if name.isdigit():
        return IntegerIndex.from_name(name)

    elif name == "" or ":" in name:
        return RangeIndex.from_name(name)

    else:
        raise ValueError(f"Invalid name: {name}")


IndexLike = int | slice | Index


@typechecked
def index_like_to_index(index: IndexLike) -> Index:
    if isinstance(index, int):
        return IntegerIndex(value=index)

    elif isinstance(index, slice):
        return RangeIndex(start=index.start, stop=index.stop)

    else:
        return index
