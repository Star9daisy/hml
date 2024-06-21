from typing import Self

import awkward as ak
import inflection
import uproot

from ..types import PathLike
from .event import Event


class DelphesEvent(Event):
    """Dict-like Delphes events with more key cases supported.

    Treat the event tree read by uproot as a dict-like object. The keys are
    expanded to snake_case, CamelCase, lower case besides the original case. For
    example, the key "FatJet.PT" can be accessed by "FatJet.PT", "fatjet.pt",
    "fat_jet.pt".

    The difference between this class and the uproot.TTree is that this class
    returns the awkward array directly without the need to call the `array()`
    method. If you want to perform operations on the event tree read by uproot,
    use `tree` attribute to access the uproot.TTree object.

    Parameters
    ----------
    tree : uproot.TTree
        The event tree read by uproot.

    Examples
    --------
    >>> import uproot
    >>> from hml.events import DelphesEvent
    >>> tree = uproot.open("tag_1_delphes_events.root")["Delphes"]
    >>> events = DelphesEvent(tree)
    >>> len(events)
    100

    >>> events["fatjet.pt"]
    <Array [[530], [632], [520], ..., [329], [490]] type='100 * var * float32'>
    >>> events["fat_jet.pt"]
    <Array [[530], [632], [520], ..., [329], [490]] type='100 * var * float32'>
    >>> events["FatJet.PT"]
    <Array [[530], [632], [520], ..., [329], [490]] type='100 * var * float32'>
    >>> events.tree["FatJet.PT"].array()
    <Array [[530], [632], [520], ..., [329], [490]] type='100 * var * float32'>

    >>> events.get("unknown_key") is None
    True
    """

    def __init__(self, tree: uproot.TTree):
        self.tree = tree

    def __len__(self) -> int:
        """The number of events"""
        return self.tree.num_entries

    def __getitem__(self, key: str):
        return self.tree[self.keys_dict[key]].array()

    @property
    def tree(self):
        """Event tree read by uproot."""
        return self._tree

    @tree.setter
    def tree(self, tree: uproot.TTree):
        self._tree = tree

        mixed_case = self.tree.keys(full_paths=False)
        snake_case = [inflection.underscore(key) for key in mixed_case]
        camel_case = [inflection.camelize(key) for key in mixed_case]
        lower_case = [key.lower() for key in mixed_case]
        keys = mixed_case + snake_case + camel_case + lower_case
        self._keys = keys

        keys_dict = {}
        keys_dict.update({key: key for key in mixed_case})
        keys_dict.update({snake: mixed for snake, mixed in zip(snake_case, mixed_case)})
        keys_dict.update({camel: mixed for camel, mixed in zip(camel_case, mixed_case)})
        keys_dict.update({lower: mixed for lower, mixed in zip(lower_case, mixed_case)})
        self._keys_dict = keys_dict

    @property
    def keys(self) -> list[str]:
        """Available keys of the Delphes events."""
        return self._keys

    @property
    def keys_dict(self) -> dict[str, str]:
        """The key mappings between Delphes event and events read by uproot."""
        return self._keys_dict

    def get(self, key: str) -> ak.Array | None:
        """Get the value according to the key."""
        if (original_key := self.keys_dict.get(key)) is not None:
            return self.tree.get(original_key).array()

    @classmethod
    def load(cls, path: PathLike) -> Self:
        """Load an event file from the given path."""
        tree = uproot.open(path + ":Delphes")
        return cls(tree)
