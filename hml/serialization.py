from importlib import import_module


def serialize(obj: object) -> dict:
    """Serialize an object to a dictionary."""
    if isinstance(obj, type):
        return {
            "module": obj.__module__,
            "class_name": obj.__name__,
        }

    else:
        return {
            "module": obj.__module__,
            "class_name": obj.__class__.__name__,
            "config": obj.config,
        }


def deserialize(obj: dict) -> object:
    """Deserialize a dictionary to an object."""
    module = import_module(obj["module"])
    cls = getattr(module, obj["class_name"])

    if "config" in obj:
        return cls.from_config(obj["config"])
    else:
        return cls
