from importlib import import_module

from typeguard import typechecked

from ..types import Serializable


@typechecked
def serialize(obj: Serializable) -> dict:
    """Convert an object to a dictionary of its configuration."""
    return {
        "module": obj.__module__,
        "class_name": obj.__class__.__name__,
        "config": obj.config,
    }


@typechecked
def deserialize(config: dict) -> Serializable:
    """Convert a dictionary of configuration to an object."""
    module = import_module(config["module"])
    cls = getattr(module, config["class_name"])
    return cls.from_config(config["config"])
