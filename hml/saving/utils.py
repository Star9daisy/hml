import importlib
import inspect
import sys

from typeguard import typechecked

from ..config import get_custom_objects_file_path


@typechecked
def import_custom_objects() -> None:
    """Import custom objects to register them."""
    CUSTOM_OBJECTS_FILE_PATH = get_custom_objects_file_path()
    if not CUSTOM_OBJECTS_FILE_PATH.exists():
        return

    sys.path.append(CUSTOM_OBJECTS_FILE_PATH.parent.as_posix())

    module = importlib.import_module(CUSTOM_OBJECTS_FILE_PATH.stem)

    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if not attribute_name.startswith("_") and inspect.isclass(attribute):
            globals()[attribute_name] = attribute
