from pathlib import Path

from typeguard import typechecked

from .types import PathLike, pathlike_to_path

CUSTOM_OBJECTS_FILE_PATH = Path("custom_objects.py")
REGISTRY_FILE_PATH = Path("registry.json")


@typechecked
def get_custom_objects_file_path() -> Path:
    """Get the path to the file containing custom objects. The default path is
    `custom_objects.py`.

    The custom objects file usually contains classes that are registered with
    the `saving.registered_object` decorator.
    """
    return CUSTOM_OBJECTS_FILE_PATH


@typechecked
def set_custom_objects_file_path(file_path: PathLike) -> None:
    """Set the path to the file containing custom objects."""
    file_path = pathlike_to_path(file_path)
    global CUSTOM_OBJECTS_FILE_PATH
    CUSTOM_OBJECTS_FILE_PATH = file_path


@typechecked
def get_registry_file_path() -> Path:
    """Get the path to the file containing the registry. The default path is
    `registry.json`.
    """
    return REGISTRY_FILE_PATH


@typechecked
def set_registry_file_path(file_path: PathLike) -> None:
    """Set the path to the file containing the registry."""
    file_path = pathlike_to_path(file_path)
    global REGISTRY_FILE_PATH
    REGISTRY_FILE_PATH = file_path
