import inspect
import re

from typeguard import typechecked

from ..types import Registrable

ALL_REGISTERED_OBJECTS = []


@typechecked
def registered_object(
    name: str | re.Pattern | None = None,
    is_for_init: bool = False,
):
    """Decorator to register an object with a name or pattern.

    Parameters
    ----------
    name : str, re.Pattern, optional
        A string or regular expression pattern. If not provided, its name is
        used.
    is_for_init : bool
        Whether to call `from_name` when a class is retrieved by the name.
        Default is False.


    Returns
    -------
    decorator
    """

    @typechecked
    def decorator(obj: Registrable):
        registered_name = obj.__name__ if name is None else name
        ALL_REGISTERED_OBJECTS.append(
            {
                "registered_name": registered_name,
                "class": obj,
                "is_for_init": is_for_init,
            }
        )

        return obj

    return decorator


@typechecked
def register(
    obj: object,
    name: str | re.Pattern | None = None,
    is_for_init: bool = False,
):
    """Register an object with a name or pattern.

    Parameters
    ----------
    obj : object
        An object to register.
    name : str, re.Pattern, optional
        A string or regular expression pattern. If not provided, its name is
        used.
    is_for_init : bool
        Whether to call `from_name` when a class is retrieved by the name.
        Default is False.
    """
    return registered_object(name, is_for_init)(obj)


@typechecked
def retrieve(name_or_object: str | object) -> object | list[dict] | None:
    """Retrieve a registered object by name or all names of a registered
    object.

    Parameters
    ----------
    name_or_object : str, type
        A string or class to retrieve

    Returns
    -------
    object, list[dict], optional
        A class or an instance if a string is provided, or a list of
        dictionaries containing the registered name and initialization status if
        a class is provided. If the object is not registered, None is returned.
    """
    if isinstance(name_or_object, str):
        name = name_or_object

        for object_dict in ALL_REGISTERED_OBJECTS:
            registered_name, cls, init = object_dict.values()
            if not re.fullmatch(registered_name, name):
                continue

            if not init:
                return cls

            return cls.from_name(name)

    else:
        obj = name_or_object
        registered_names = []

        for object_dict in ALL_REGISTERED_OBJECTS:
            registered_name, cls, init = object_dict.values()
            if obj != cls:
                continue

            registered_names.append(
                {
                    "registered_name": registered_name,
                    "is_for_init": init,
                }
            )

        return registered_names
