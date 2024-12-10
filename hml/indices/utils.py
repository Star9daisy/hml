from importlib import import_module

from .base import Index, typechecked


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
