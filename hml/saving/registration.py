import inspect
import re

from inflection import underscore
from typeguard import typechecked

from ..config import get_custom_objects_file_path
from ..types import Registrable

BUILTIN_REGISTERED_OBJECTS = []
CUSTOM_REGISTERED_OBJECTS = []


@typechecked
def registered_object(name: str | None = None):
    """Decorator to register a name for a class or an instance.

    Parameters
    ----------
    name : str, optional
        A string or a regular expression. If not provided, the class name will
        be used if the object is a class, or the name attribute will be used if
        the object is an instance.

    Returns
    -------
    decorator
    """

    @typechecked
    def decorator(obj: Registrable):
        # Class or instance?
        if inspect.isclass(obj):
            registered_name = underscore(obj.__name__) if name is None else name
            class_ = obj
        else:
            registered_name = obj.name if name is None else name
            class_ = obj.__class__

        # Custom or built-in object?
        if obj.__module__ == get_custom_objects_file_path().stem:
            registered_objects = CUSTOM_REGISTERED_OBJECTS
        else:
            registered_objects = BUILTIN_REGISTERED_OBJECTS

        # Add the name-class dictionary to the list
        registered_objects.append(
            (
                {
                    "registered_name": registered_name,
                    "class": class_,
                }
            )
        )
        return obj

    return decorator


@typechecked
def register(obj: Registrable, name: str | None = None):
    """Register an object with a name.

    Parameters
    ----------
    obj : Registrable class or instance
        A serializable object to register.
    name : str, optional
        A string or a regular expression. If not provided, the class name will
        be used if the object is a class, or the name attribute will be used if
        the object is an instance.
    """
    return registered_object(name)(obj)


@typechecked
def retrieve(name_or_class: str | Registrable) -> object | list[str] | None:
    """Retrieve a registered object by name or all names of a registered class.

    Parameters
    ----------
    name_or_class : str or Registrable
        A string (or a regular expression) or a class to retrieve.

    Returns
    -------
    object, list[dict], optional
        An instance if a string is provided, or a list of registered
        names. If the name or class is not registered, None or an empty list is
        returned.
    """
    if isinstance(name_or_class, str):
        name = name_or_class

        for object_dict in [*CUSTOM_REGISTERED_OBJECTS, *BUILTIN_REGISTERED_OBJECTS]:
            registered_name, cls = object_dict.values()

            if (match := re.fullmatch(registered_name, name)) is not None:
                config = match.groupdict()
                return cls.from_config(config)

    else:
        class_ = name_or_class
        registered_names = []

        for object_dict in [*CUSTOM_REGISTERED_OBJECTS, *BUILTIN_REGISTERED_OBJECTS]:
            registered_name, cls = object_dict.values()

            if class_ == cls:
                registered_names.append(registered_name)

        return registered_names
