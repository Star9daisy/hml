from importlib import import_module

from typeguard import typechecked

from ..types import Type
from .base import Index
from .integer import IntegerIndex
from .range import RangeIndex

BUILTIN_INDICES: list[Type[Index]] = [IntegerIndex, RangeIndex]


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
def retrieve(name: str) -> Index:
    for cls in BUILTIN_INDICES:
        if cls.PATTERN.fullmatch(name):
            return cls.from_name(name)

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
