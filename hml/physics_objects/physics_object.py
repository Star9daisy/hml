import re
from abc import ABC, abstractmethod
from typing import Self

import awkward as ak
import inflection
from typeguard import typechecked

from ..events import ROOTEvents
from ..operations.awkward_ops import pad_none
from ..types import AwkwardArray, Index, index_to_str, str_to_index


@typechecked
class Single(ABC):
    def __init__(
        self,
        key: str | None = None,
        index: Index | None = None,
        class_alias: str | None = None,
    ) -> None:
        self._key = key
        self._index = index
        self._array = None
        self._class_alias = class_alias

        self._need_update_cached_array = False

    def __repr__(self) -> str:
        if not self.array.fields:
            return f"{self.name} -> (not read yet)"

        fields = ", ".join(self.array.fields)
        return f"{self.name} -> ({fields})"

    @property
    def key(self) -> str:
        if hasattr(self, "_cached_key"):
            return self._cached_key

        if self._key is None:
            self._cached_key = self.__class__.__name__
        else:
            self._cached_key = self._key

        self._cached_key = inflection.underscore(self._cached_key)

        return self._cached_key

    @property
    def index(self) -> Index:
        if hasattr(self, "_cached_index"):
            return self._cached_index

        if self._index is None:
            self._cached_index = slice(None)
        else:
            self._cached_index = self._index

        return self._cached_index

    @property
    def array(self) -> AwkwardArray:
        if hasattr(self, "_cached_array") and not self._need_update_cached_array:
            return self._cached_array

        if self._array is None:
            self._cached_array = ak.Array([])
        else:
            self._cached_array = self._array

        self._need_update_cached_array = False

        return self._cached_array

    @property
    def class_alias(self) -> str | None:
        return self._class_alias

    @abstractmethod
    def get_array(self, events: ROOTEvents) -> AwkwardArray: ...

    def read(self, events: ROOTEvents) -> Self:
        array = self.get_array(events)

        if isinstance(self.index, int):
            target = self.index + 1
        elif self.index.stop is not None:
            target = self.index.stop
        else:
            target = None

        if target is not None:
            padded = pad_none(array, target, 1)
        else:
            padded = array

        self._array = padded[:, self.index]

        try:
            self._array = ak.to_regular(self._array, axis=None)
        except Exception:
            pass

        # After reading events, the cached array needs to be updated
        self._need_update_cached_array = True
        return self

    @property
    def name(self) -> str:
        if self._class_alias is not None:
            return f"{self._class_alias}{index_to_str(self.index)}"

        return f"{self.key}{index_to_str(self.index)}"

    @classmethod
    def from_name(cls, name: str) -> Self:
        class_alias, index = [], []

        match = re.fullmatch(r"([A-Za-z_]+)(\d*:?\d*)", name)
        key = class_alias = match.group(1)
        index = str_to_index(match.group(2))

        return cls(key, index, class_alias)

    @property
    def config(self) -> dict:
        return {
            "key": self.key,
            "index": index_to_str(self.index),
            "class_alias": self.class_alias,
        }

    @classmethod
    def from_config(cls, config: dict) -> Self:
        config["index"] = str_to_index(config["index"])
        return cls(**config)


@typechecked
class Nested(ABC):
    def __init__(
        self,
        keys: list[str],
        indices: list[Index] | None = None,
        class_alias: str | None = None,
    ) -> None:
        self._keys = keys
        self._indices = indices
        self._array = None
        self._class_alias = class_alias

        self._need_update_cached_array = False

    def __repr__(self) -> str:
        if not self.array.fields:
            return f"{self.name} -> (not read yet)"

        fields = ", ".join(self.array.fields)
        return f"{self.name} -> ({fields})"

    @property
    def keys(self) -> list[str]:
        if hasattr(self, "_cached_keys"):
            return self._cached_keys

        self._cached_keys = [inflection.underscore(i) for i in self._keys]

        return self._cached_keys

    @property
    def indices(self) -> list[Index]:
        if hasattr(self, "_cached_indices"):
            return self._cached_indices

        if self._indices is None:
            self._cached_indices = [slice(None)] * len(self.keys)
        else:
            self._cached_indices = self._indices

        return self._cached_indices

    @property
    def array(self) -> AwkwardArray:
        if hasattr(self, "_cached_array") and not self._need_update_cached_array:
            return self._cached_array

        if self._array is None:
            self._cached_array = ak.Array([])
        else:
            self._cached_array = self._array

        self._need_update_cached_array = False

        return self._cached_array

    @property
    def class_alias(self) -> str | None:
        return self._class_alias

    @abstractmethod
    def get_array(self, events: ROOTEvents) -> AwkwardArray: ...

    def read(self, events: ROOTEvents) -> Self:
        array = self.get_array(events)

        for i, index in enumerate(self.indices, start=1):
            if isinstance(index, int):
                target = index + 1
            elif index.stop is not None:
                target = index.stop
            else:
                target = None

            if target is not None:
                array = pad_none(array, target, i)

        self._array = array[tuple([slice(None), *self.indices])]

        try:
            self._array = ak.to_regular(self._array, axis=None)
        except Exception:
            pass

        # # After reading events, the cached array needs to be updated
        self._need_update_cached_array = True
        return self

    @property
    def name(self) -> str:
        keys = self.keys
        indices = [index_to_str(index) for index in self.indices]

        if self.class_alias is not None:
            print(0)
            aliases = keys[:-1] + [self.class_alias]
            name = ".".join(alias + index for alias, index in zip(aliases, indices))

        else:
            name = ".".join(key + index for key, index in zip(keys, indices))

        return name

    @classmethod
    def from_name(cls, name: str) -> Self:
        parts = name.split(".")

        keys, indices = [], []
        for i, part in enumerate(parts):
            match = re.fullmatch(r"([A-Za-z_]+)(\d*:?\d*)", part)
            keys.append(match.group(1))
            indices.append(str_to_index(match.group(2)))

            if i + 1 == len(parts):
                print(1)
                class_alias = match.group(1)

        return cls(keys, indices, class_alias)

    @property
    def config(self) -> dict:
        return {
            "keys": self.keys,
            "indices": [index_to_str(i) for i in self.indices],
            "class_alias": self.class_alias,
        }

    @classmethod
    def from_config(cls, config: dict) -> Self:
        config["indices"] = [str_to_index(i) for i in config["indices"]]
        return cls(**config)
