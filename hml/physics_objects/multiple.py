from __future__ import annotations

from typing import Any

from .collective import Collective
from .collective import is_collective
from .nested import Nested
from .nested import is_nested
from .physics_object import PhysicsObject
from .single import Single
from .single import is_single


def is_multiple(name: str, supported_types: list[str] | None = None) -> bool:
    """Check if a name corresponds to a multiple physics object.

    Parameters
    ----------
    name : str
        The name of a physics object.
    supported_types : list[str] | None
        Supported types of the physics objects. Valid values are "single",
        "collective", and "nested". If `None`, all types are supported.

    Returns
    -------
    result : bool

    Examples
    --------
    >>> is_multiple("Jet0,Jet1")
    True

    >>> is_multiple("Jet0,Jet1", ["single", "collective"])
    True
    """
    try:
        obj = Multiple.from_name(name)

    except Exception:
        return False

    if supported_types is None:
        return True

    supported_classes = []
    for classname in supported_types:
        if classname.lower() == "single":
            supported_classes.append(Single)
        elif classname.lower() == "collective":
            supported_classes.append(Collective)
        elif classname.lower() == "nested":
            supported_classes.append(Nested)
        else:
            raise ValueError(
                f"Invalid supported type '{classname}'. "
                f"Valid values are 'single', 'collective', and 'nested'."
            )

    for phyobj in obj.physics_objects:
        if not isinstance(phyobj, tuple(supported_classes)):
            return False

    return True


class Multiple(PhysicsObject):
    """The data class that represents multiple physics objects.

    For example, three leading jets, all jets and all electrons, constituents of
    the leading jet and sub-leading jet, etc.

    Parameters
    ----------
    physics_objects : list[Single | Collective | Nested]
        A list of physics objects.

    Attributes
    ----------
    name : str
        The name of the physics object.
    value : list[Any] | None
        The fetched values of the physics objects.

    Examples
    --------
    Create a multiple physics object by its physics objects:
    >>> Multiple(
    ...     physics_objects=[
    ...         Single(branch="Jet", index=0),
    ...         Collective(branch="Jet", start=1, stop=3),
    ...         Nested(
    ...             main=Single(branch="Jet", index=0),
    ...             sub=Collective(branch="Constituents", stop=100),
    ...         ),
    ...     ]
    ... )
    Multiple(name='Jet0,Jet1:3,Jet0.Constituents:100', value=None)

    Create a multiple physics object from its name:
    >>> Multiple.from_name("Jet0,Jet1:3,Jet0.Constituents:100")
    Multiple(name='Jet0,Jet1:3,Jet0.Constituents:100', value=None)

    Read an event to fetch the leading jet and the  sub-leading jet:
    >>> obj = Multiple(
    ...     physics_objects=[
    ...         Single(branch="Jet", index=0),
    ...         Single(branch="Jet", index=1),
    ...     ]
    ... )
    >>> obj.read_ttree(event)
    >>> obj
    Multiple(name='Jet0,Jet1', value=[<cppyy.gbl.Jet object at 0xa574af0>, <cppyy.gbl.Jet object at 0xa575120>])

    Use `physics_objects` to show details:
    >>> obj.physics_objects
    [Single(name='Jet0', value=<cppyy.gbl.Jet object at 0xa574af0>),
     Single(name='Jet1', value=<cppyy.gbl.Jet object at 0xa575120>)]
    """

    def __init__(self, physics_objects: list[Single | Collective | Nested]):
        self.physics_objects = physics_objects

    def read_ttree(self, event: Any) -> Multiple:
        """Read an event to fetch the value.

        Parameters
        ----------
        event : TTree
            An event read by PyROOT.

        Returns
        -------
        self : Multiple

        Examples
        --------
        Read an event to fetch the leading two jets:
        >>> obj = Multiple.from_name("Jet0,Jet1")
        >>> obj.read_ttree(event)
        >>> obj.value
        [<cppyy.gbl.Jet object at 0xa574af0>, <cppyy.gbl.Jet object at 0xa575120>]

        Read an event to fetch the first 5 constituents of the leading two jets:
        >>> obj = Multiple.from_name("Jet0.Constituents:5,Jet1.Constituents:5")
        >>> obj.read_ttree(event)
        >>> obj.value
        [[[<cppyy.gbl.Tower object at 0x9b6ab30>,
           <cppyy.gbl.Track object at 0x9528c10>,
           <cppyy.gbl.Track object at 0x9528fd0>,
           <cppyy.gbl.Tower object at 0x9b6ac50>,
           <cppyy.gbl.Track object at 0x9528a30>]],
         [[<cppyy.gbl.Tower object at 0x9b6a7d0>,
           <cppyy.gbl.Track object at 0x95280d0>,
           <cppyy.gbl.Tower object at 0x9b6a980>,
           <cppyy.gbl.Track object at 0x89fb410>,
           <cppyy.gbl.Track object at 0x9527b30>]]]

        ! For any failure cases, check the docs of `Single.read_ttree`,
        `Collective.read_ttree` and `Nested.read_ttree`.
        """
        self._value = []

        for phyobj in self.physics_objects:
            phyobj.read_ttree(event)
            self._value.append(phyobj.value)

        return self

    @property
    def name(self) -> str:
        return ",".join([i.name for i in self.physics_objects])

    @property
    def value(self) -> Any:
        return [i.value for i in self.physics_objects]

    @property
    def config(self) -> dict[str, Any]:
        return {
            f"physics_object_{i}": {
                "class_name": physics_object.__class__.__name__,
                "config": physics_object.config,
            }
            for i, physics_object in enumerate(self.physics_objects)
        }

    @classmethod
    def from_name(cls, name: str) -> Multiple:
        """Create a multiple physics object from an identifier.

        Parameters
        ----------
        name : str

        Returns
        -------
        physics object : Multiple

        Raises
        ------
        ValueError
            If the name is invalid.
        """
        if "," not in name:
            raise ValueError(f"Invalid name '{name}' for {cls.__name__}")

        physics_objects = []
        for i in name.split(","):
            if is_single(i):
                physics_objects.append(Single.from_name(i))
            elif is_collective(i):
                physics_objects.append(Collective.from_name(i))
            elif is_nested(i):
                physics_objects.append(Nested.from_name(i))
            else:
                raise ValueError(f"Invalid '{name}' for {cls.__name__}")

        return cls(physics_objects)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> Multiple:
        class_dict = {
            "Single": Single,
            "Collective": Collective,
            "Nested": Nested,
        }
        physics_objects = []

        for physics_object in config:
            physics_object_cls = class_dict[config[physics_object]["class_name"]]
            physics_objects.append(
                physics_object_cls.from_config(config[physics_object]["config"])
            )

        return cls(physics_objects)
