from __future__ import annotations

from typing import Any

from .physics_object import PhysicsObject
from .single import Single


def is_collective(object: str | PhysicsObject) -> bool:
    """Check if an identifier or an instance corresponds to a collective physics
    object.

    Parameters
    ----------
    identifier : str | PhysicsObject
        A unique string for a physics object or an instance of a physics object.

    Returns
    -------
    result : bool

    Examples
    --------
    >>> is_collective("Jet:")
    True

    >>> is_collective("Jet0") # Single
    False

    >>> is_collective("Jet0.Constituents:100") # Nested
    False

    >>> is_collective("Jet0,Jet1") # Multiple
    False
    """
    if isinstance(object, PhysicsObject):
        return isinstance(object, Collective)

    try:
        Collective.from_id(object)
        return True

    except Exception:
        return False


class Collective(PhysicsObject):
    """A collective physics object.

    It represents a collection of physics objects. For example, the leading
    three jets, all the constituents of the leading jet, etc.

    Parameters
    ----------
    name : str
        The name of the physics object.
    start : int
        The starting index of the physics object.
    stop : int
        The stopping index of the physics object.

    Examples
    --------
    Create a collective physics object by its name, starting and stopping indices:
    >>> obj = Collective("Jet", 1, 2)
    >>> obj.name, obj.start, obj.stop
    ('Jet', 1, 2)

    Four cases for the starting and stopping indices:
    1. Default is 0 and -1, which means all objects:
    >>> Collective("Jet")
    Jet:

    2. Starting index is a positive integer:
    >>> Collective("Jet", 1)
    Jet1:

    3. Stopping index is a positive integer:
    >>> Collective("Jet", stop=2)
    Jet:2

    4. Both starting and stopping indices are positive integers:
    >>> Collective("Jet", 1, 2)
    Jet1:2

    It is represented by the identifier:
    >>> obj = Collective("Jet", 1, 2)
    >>> obj
    Jet1:2
    >>> obj.identifier
    Jet1:2

    Create a collective physics object from an identifier:
    >>> Collective.from_identifier("Jet1:2")
    Jet1:2
    """

    def __init__(self, field: str, start: int = 0, stop: int = -1):
        self.field = field
        self.start = start
        self.stop = stop
        self.objects = []

    def read_ttree(self, ttree: Any) -> Collective:
        """Read an entry to fetch the objects.

        Every time it is called, the objects will be cleared and re-filled.

        Parameters
        ----------
        entry : Any
            An event or a branch read by PyROOT.

        Returns
        -------
        self : Collective

        Raises
        ------
        ValueError
            If the name is not a valid attribute of the entry.

        Examples
        --------
        Read an event to fetch all jets:
        >>> Collective("Jet", 0, 3).read(event).objects
        [<cppyy.gbl.Jet object at 0x8ec8850>,
        <cppyy.gbl.Jet object at 0x8ec8e80>,
        <cppyy.gbl.Jet object at 0x8ec94b0>]

        Read the leading jet to fetch all constituents:
        >>> len(Collective("Constituents").read(event.Jet[0]).objects)
        20

        ! If the starting index is out of range, an empty list will be returned:
        >>> Collective("Jet", 100).read(event).objects
        []

        ! If the stopping index is out of range, `None` will be filled to ensure
        the length of the objects:
        >>> Collective("Jet", 3, 6).read(event).objects
        [<cppyy.gbl.Jet object at 0x920a1f0>,
        <cppyy.gbl.Jet object at 0x920a820>,
        None]
        """
        self.objects = []

        object = getattr(ttree, self.field, None)
        n_entries = object.GetEntries() if object is not None else 0
        stop = self.stop if self.stop != -1 else n_entries

        for i in range(self.start, stop):
            single_objects = Single(self.field, i).read_ttree(ttree).objects
            self.objects += single_objects if len(single_objects) != 0 else [None]

        return self

    @property
    def id(self) -> str:
        """The unique string for a collective physics object.

        It consists of the name, the starting and stopping indices, and a colon`:`.

        Examples
        --------
        >>> Collective("Jet").identifier
        Jet:
        >>> Collective("Jet", 1).identifier
        Jet1:
        >>> Collective("Jet", stop=2).identifier
        Jet:2
        >>> Collective("Jet", 1, 2).identifier
        Jet1:2
        """
        if self.start == 0 and self.stop == -1:
            return f"{self.field}:"

        elif self.start == 0:
            return f"{self.field}:{self.stop}"

        elif self.stop == -1:
            return f"{self.field}{self.start}:"

        else:
            return f"{self.field}{self.start}:{self.stop}"

    @classmethod
    def from_id(cls, id: str) -> Collective:
        """Create a collective physics object from an identifier.

        It decomposes the identifier into a name, a starting index, and a stopping
        index to construct a collective physics object.

        Parameters
        ----------
        identifier : str
            A unique string for a physics object.

        Returns
        -------
        physics object : Collective

        Raises
        ------
        ValueError
            No colon`:` or there's any of comma`,` or period`.`.
        """
        if ":" not in id:
            raise ValueError(
                "Invalid identifier for Collective. The colon':' is missing.\n"
                "Correct the identifier like 'Jet:'."
            )

        if "," in id:
            raise ValueError(
                "Invalid identifier for Collective. The comma',' indicates it "
                "corresponds to a multiple physics object.\n"
                f"Use `Multiple.from_identifier('{id}')` instead."
            )

        if "." in id:
            raise ValueError(
                "Invalid identifier for Collective. The period'.' indicates it "
                "corresponds to a nested physics object.\n"
                f"Use `Nested.from_identifier('{id}')` instead."
            )

        first, second = id.split(":")
        start = "".join(filter(lambda x: x.isdigit(), first))
        name = first.replace(start, "")
        start = int(start) if start != "" else 0
        stop = int(second) if second != "" else -1

        return cls(name, start, stop)

    @property
    def config(self) -> dict[str, Any]:
        """The configurations for serialization"""
        return {
            "classname": "Collective",
            "field": self.field,
            "start": self.start,
            "stop": self.stop,
        }

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> Collective:
        """Create a collective physics object from configurations.

        Parameters
        ----------
        config : dict

        Returns
        -------
        physics object : Collective

        Raises
        ------
        ValueError
            If `classname` in the configurations is not "Collective".
        """
        if config["classname"] != "Collective":
            raise ValueError(
                f"Invalid classname {config.get('classname')}. Expected 'Collective'."
            )

        return cls(config["field"], config["start"], config["stop"])
